"""Terminales: Bash (Linux/macOS/Git Bash), PowerShell y CMD (Windows). 3 etapas."""
from ..generador import K
from .terminal_e45 import E4, E5

E1 = [
K("Qué es la terminal", d="programa de texto donde escribes órdenes para el sistema", u="controlar el computador escribiendo comandos en vez de usar el mouse",
  mas="La terminal (o consola) muestra un indicador llamado prompt y espera que escribas una orden. Al pulsar Enter, el intérprete de comandos (shell) la ejecuta y muestra el resultado. Bash, zsh, PowerShell y CMD son intérpretes distintos.",
  k=["La terminal recibe órdenes escritas con el teclado.", "El shell es el programa que interpreta cada orden.", "Cada orden se ejecuta al pulsar Enter."],
  sit="Quieres manejar archivos y programas escribiendo órdenes de texto en lugar de hacer clic. ¿Qué herramienta abres?",
  cod="""# El prompt espera tu orden; echo repite el texto
echo "Hola desde la terminal\"""", h="muestra un saludo escrito por la orden echo",
  pr=("El programa que interpreta lo que escribes en la terminal se llama ___. (5 letras)", "shell"),
  pr2=("Para ejecutar una orden en la terminal pulsas la tecla ___. (5 letras)", "enter"),
  ec="escribir la orden y olvidar pulsar Enter para ejecutarla", out="Hola desde la terminal"),
K("pwd", d="orden que muestra la carpeta en la que estás", u="saber en qué lugar del sistema de archivos trabajas",
  mas="Toda terminal trabaja siempre dentro de una carpeta llamada directorio actual. pwd (print working directory) imprime su ruta completa. En PowerShell también funciona pwd (alias de Get-Location) y en CMD se usa cd sin argumentos.",
  k=["pwd imprime la ruta del directorio actual.", "Las órdenes con rutas relativas parten del directorio actual.", "En CMD el equivalente de pwd es cd sin argumentos."],
  sit="Abriste la terminal y no sabes en qué carpeta estás parado. ¿Qué orden escribes?",
  cod="""# ¿Dónde estoy?
pwd""", h="imprime la ruta de la carpeta actual",
  pr=("La orden de Bash que imprime la carpeta actual es ___. (3 letras)", "pwd"),
  pr2=("La carpeta donde trabaja la terminal se llama directorio ___. (6 letras)", "actual"),
  ec="crear archivos sin revisar antes en qué carpeta estás", out="/home/ana/proyectos"),
K("ls", d="orden que lista el contenido de una carpeta", u="ver qué archivos y carpetas hay antes de trabajar con ellos",
  mas="ls muestra los nombres de lo que hay en la carpeta actual o en la que indiques. Con -l muestra detalles (permisos, tamaño, fecha) y con -a incluye los archivos ocultos que empiezan por punto. En PowerShell ls es alias de Get-ChildItem y en CMD se usa dir.",
  k=["ls muestra los archivos de una carpeta.", "La opción -a de ls incluye los archivos ocultos.", "En CMD se usa dir en lugar de ls."],
  sit="Necesitas ver qué archivos hay en la carpeta del proyecto, incluidos los ocultos como .gitignore. ¿Qué orden usas?",
  cod="""# Lista todo, también lo oculto, con detalles
ls -la""", h="lista con detalles todos los archivos, incluidos los ocultos",
  pr=("La opción de ls que muestra los archivos ocultos es -___. (1 letra)", "a"),
  pr2=("En la terminal CMD de Windows, el equivalente de ls es ___. (3 letras)", "dir"),
  ec="pensar que una carpeta está vacía porque ls sin -a no muestra lo oculto", out=".  ..  .gitignore  index.html  css"),
K("cd", d="orden que cambia de carpeta", u="moverte entre carpetas del proyecto desde la terminal",
  mas="cd ruta entra a esa carpeta. cd .. sube a la carpeta padre, cd ~ va a tu carpeta personal y cd - vuelve a la anterior. Las rutas pueden ser relativas (desde donde estás) o absolutas (desde la raíz). Funciona igual en Bash, PowerShell y CMD.",
  k=["cd .. sube a la carpeta padre.", "cd ~ lleva a la carpeta personal en Bash.", "cd acepta rutas relativas y absolutas."],
  sit="Estás en la carpeta css y quieres volver a la carpeta del proyecto que la contiene. ¿Qué orden escribes?",
  cod="""cd css      # entra a css
cd ..       # vuelve a la carpeta padre
pwd""", h="entra a una carpeta y vuelve a la anterior",
  pr=("Para subir a la carpeta padre escribes cd ___. (2 caracteres)", ".."),
  pr2=("En Bash, el símbolo ___ representa tu carpeta personal. (1 carácter)", "~"),
  ec="escribir cd.. sin espacio en Bash, donde no funciona", out="/home/ana/proyecto"),
K("mkdir y touch", d="órdenes para crear carpetas y archivos vacíos", u="armar la estructura de un proyecto sin salir de la terminal",
  mas="mkdir crea una carpeta; con -p crea también las intermedias que falten. touch crea un archivo vacío (o actualiza su fecha si ya existe). En PowerShell se usa New-Item y mkdir también existe; en CMD, mkdir o md crean carpetas.",
  k=["mkdir crea carpetas nuevas.", "mkdir -p crea también las carpetas intermedias.", "touch crea un archivo vacío en Bash."],
  sit="Quieres crear de una vez la carpeta src/componentes aunque src todavía no exista. ¿Qué orden usas?",
  cod="""mkdir -p src/componentes   # crea src y componentes
touch src/main.js          # archivo vacío
ls src""", h="crea carpetas anidadas y un archivo vacío",
  pr=("La opción de mkdir que crea las carpetas intermedias es -___. (1 letra)", "p"),
  pr2=("En Bash, la orden que crea un archivo vacío es ___. (5 letras)", "touch"),
  ec="usar mkdir para crear archivos en lugar de carpetas", out="componentes  main.js"),
K("cp, mv y rm", d="órdenes para copiar, mover o renombrar y borrar archivos", u="organizar archivos rápidamente desde la terminal",
  mas="cp origen destino copia; mv origen destino mueve o renombra; rm borra. Para carpetas se usa -r (recursivo). rm no manda a la papelera: lo borrado no se recupera, por eso conviene revisar dos veces. En PowerShell existen Copy-Item, Move-Item y Remove-Item; en CMD, copy, move y del.",
  k=["mv también sirve para renombrar archivos.", "rm borra sin pasar por la papelera.", "cp -r copia carpetas completas."],
  sit="Te equivocaste en el nombre de un archivo y quieres cambiarlo de estilo.css a estilos.css. ¿Qué orden usas?",
  cod="""cp index.html copia.html     # copia
mv estilo.css estilos.css    # renombra
rm copia.html                # borra (¡sin papelera!)
ls""", h="copia, renombra y borra archivos",
  pr=("La orden de Bash que mueve o renombra archivos es ___. (2 letras)", "mv"),
  pr2=("Para copiar una carpeta entera con cp se usa la opción -___. (1 letra)", "r"),
  ec="usar rm -rf sin revisar la ruta y borrar lo que no querías", out="estilos.css  index.html"),
K("cat y redirección", d="mostrar el contenido de archivos y enviar la salida a un archivo", u="leer archivos y guardar resultados de órdenes",
  mas="cat archivo muestra su contenido. El operador > guarda la salida de una orden en un archivo (lo reemplaza) y >> la agrega al final. En PowerShell, Get-Content (alias cat) lee archivos; en CMD se usa type. Los operadores > y >> funcionan en los tres.",
  k=["cat muestra el contenido de un archivo.", "El operador > reemplaza el contenido del archivo.", "El operador >> agrega al final sin borrar."],
  sit="Quieres agregar una línea nueva al final de notas.txt sin borrar lo que ya tenía. ¿Qué operador usas?",
  cod="""echo "primera" > notas.txt    # crea o reemplaza
echo "segunda" >> notas.txt   # agrega al final
cat notas.txt""", h="escribe dos líneas en un archivo y lo muestra",
  pr=("El operador que agrega texto al final de un archivo es ___. (2 caracteres)", ">>"),
  pr2=("En CMD, la orden que muestra el contenido de un archivo es ___. (4 letras)", "type"),
  ec="usar > cuando querías agregar y borrar el contenido anterior", out="primera\nsegunda"),
K("Autocompletar e historial", d="atajos del teclado para escribir menos en la terminal", u="trabajar más rápido y sin errores de escritura",
  mas="La tecla Tab completa nombres de archivos, carpetas y órdenes; si hay varias opciones, dos Tab las muestran. Las flechas arriba y abajo recorren las órdenes anteriores y history las lista. Ctrl+C detiene la orden que se está ejecutando y Ctrl+L limpia la pantalla.",
  k=["La tecla Tab completa nombres de archivos.", "La flecha arriba recupera la orden anterior.", "Ctrl+C detiene el programa que se está ejecutando."],
  sit="Un programa se quedó ejecutándose sin terminar y quieres detenerlo desde la terminal. ¿Qué atajo usas?",
  cod="""# Escribe "cd pro" y pulsa Tab → cd proyecto/
history | tail -n 3   # últimas órdenes""", h="usa el historial para ver las últimas órdenes",
  pr=("La tecla que completa nombres en la terminal es ___. (3 letras)", "tab"),
  pr2=("Para detener un programa en ejecución pulsas Ctrl+___. (1 letra)", "c"),
  ec="escribir rutas largas a mano y equivocarse en una letra", out="  41  cd proyecto\n  42  ls\n  43  history | tail -n 3"),
]

E2 = [
K("Rutas absolutas y relativas", d="dos formas de escribir la ubicación de un archivo", u="indicar exactamente qué archivo o carpeta quieres usar",
  mas="Una ruta absoluta empieza en la raíz: /home/ana/app en Linux o C:\\Users\\Ana\\app en Windows. Una relativa parte del directorio actual: css/estilos.css o ../datos. El punto . es la carpeta actual y .. la carpeta padre.",
  k=["Una ruta absoluta empieza en la raíz del disco.", "Una ruta relativa parte del directorio actual.", "El punto solo representa la carpeta actual."],
  sit="Quieres referirte a un archivo escribiendo su ubicación completa desde la raíz, sin depender de dónde estés. ¿Qué tipo de ruta usas?",
  cod="""cat /home/ana/app/index.html   # absoluta
cat ./index.html               # relativa (desde aquí)
cat ../otro/readme.md          # relativa (carpeta padre)""", h="lee archivos con rutas absolutas y relativas",
  pr=("Una ruta que empieza en la raíz del disco es ___. (8 letras)", "absoluta"),
  pr2=("En una ruta, el símbolo que representa la carpeta actual es ___. (1 carácter)", "."),
  ec="usar una ruta relativa desde la carpeta equivocada", out="<h1>Mi app</h1>"),
K("Pipes", d="operador | que pasa la salida de una orden a otra", u="combinar órdenes pequeñas para resolver tareas grandes",
  mas="El pipe | conecta órdenes: la salida de la primera es la entrada de la segunda. Por ejemplo ls | wc -l cuenta archivos y cat log.txt | grep error filtra líneas. PowerShell también usa |, pero pasa objetos en lugar de texto.",
  k=["El pipe pasa la salida de una orden a la siguiente.", "Se pueden encadenar varios pipes seguidos.", "En PowerShell el pipe pasa objetos, no solo texto."],
  sit="Quieres contar cuántos archivos hay en una carpeta usando la salida de ls como entrada de otra orden. ¿Qué operador usas?",
  cod="""ls | wc -l           # cuenta los archivos
cat app.log | grep error | head -n 2""", h="cuenta archivos y filtra las primeras líneas con error",
  pr=("El operador que conecta dos órdenes se llama ___. (4 letras)", "pipe", "tubería", "tuberia"),
  pr2=("El símbolo del pipe en la terminal es ___. (1 carácter)", "|"),
  ec="confundir el pipe | con la redirección > a un archivo", out="12\nerror: sin conexión\nerror: archivo no encontrado"),
K("grep", d="orden que busca texto dentro de archivos o salidas", u="encontrar rápido dónde aparece una palabra",
  mas="grep patrón archivo muestra las líneas que contienen el patrón. -i ignora mayúsculas, -n muestra el número de línea y -r busca en todas las subcarpetas. En PowerShell el equivalente es Select-String y en CMD findstr.",
  k=["grep muestra las líneas que contienen un texto.", "grep -r busca dentro de todas las subcarpetas.", "En PowerShell se usa Select-String para buscar texto."],
  sit="Quieres saber en qué archivos del proyecto aparece la palabra TODO, buscando en todas las subcarpetas. ¿Qué orden usas?",
  cod="""grep -rn "TODO" src/   # busca en src y subcarpetas, con número de línea""", h="busca TODO en todos los archivos de src mostrando la línea",
  pr=("La opción de grep que busca en todas las subcarpetas es -___. (1 letra)", "r"),
  pr2=("En CMD, la orden equivalente a grep es ___. (7 letras)", "findstr"),
  ec="olvidar -i y no encontrar el texto por las mayúsculas", out="src/app.js:12:// TODO: validar el formulario"),
K("Variables de entorno", d="valores con nombre que el sistema comparte con los programas", u="configurar programas sin escribir claves en el código",
  mas="PATH, HOME y USER son variables de entorno. En Bash se leen con $NOMBRE y se crean con export NOMBRE=valor. En PowerShell se leen con $env:NOMBRE y en CMD con %NOMBRE%. Las apps suelen leer claves y puertos desde aquí o desde un archivo .env.",
  k=["Las variables de entorno configuran a los programas.", "En Bash se leen escribiendo $ antes del nombre.", "En PowerShell se leen con $env: antes del nombre."],
  sit="Tu app necesita una clave secreta y no quieres escribirla dentro del código fuente. ¿Dónde la guardas?",
  cod="""export PUERTO=3000     # crea la variable
echo "Puerto: $PUERTO\"""", h="crea una variable de entorno y la muestra",
  pr=("En Bash, para crear una variable de entorno se usa ___ NOMBRE=valor. (6 letras)", "export"),
  pr2=("En PowerShell, la variable PATH se lee como $___:PATH. (3 letras)", "env"),
  ec="subir a GitHub claves secretas escritas en el código", out="Puerto: 3000"),
K("PATH", d="variable con las carpetas donde el sistema busca los programas", u="poder ejecutar programas escribiendo solo su nombre",
  mas="Cuando escribes node o git, la terminal busca ese programa en cada carpeta de PATH, en orden. Si un programa no está en ninguna, aparece «command not found» (Bash) o «no se reconoce como un comando» (Windows). Instalar un programa suele agregar su carpeta a PATH.",
  k=["PATH guarda carpetas donde se buscan programas.", "Si un programa no está en PATH, no se encuentra al escribir su nombre.", "Instalar herramientas suele agregar su carpeta a PATH."],
  sit="Instalaste Node pero la terminal dice que «node» no se reconoce como un comando. ¿Qué variable revisas?",
  cod="""echo $PATH        # carpetas donde se buscan programas
which node        # dónde está node""", h="muestra PATH y la ubicación del programa node",
  pr=("La variable con las carpetas donde se buscan los programas es ___. (4 letras)", "path"),
  pr2=("En Bash, la orden que dice dónde está un programa es ___. (5 letras)", "which"),
  ec="no reabrir la terminal después de cambiar PATH", out="/usr/local/bin:/usr/bin:/bin\n/usr/local/bin/node"),
K("Permisos y sudo", d="control de quién puede leer, escribir o ejecutar un archivo", u="proteger archivos y ejecutar tareas de administrador cuando hace falta",
  mas="En Linux y macOS cada archivo tiene permisos r (leer), w (escribir) y x (ejecutar) para el dueño, el grupo y los demás. chmod +x script.sh lo vuelve ejecutable y sudo ejecuta una orden como administrador. En Windows se abre la terminal «como administrador».",
  k=["chmod +x vuelve ejecutable un archivo.", "sudo ejecuta una orden con permisos de administrador.", "La letra r en los permisos significa lectura."],
  sit="Escribiste un script instalar.sh y al ejecutarlo dice «Permiso denegado». ¿Qué orden lo vuelve ejecutable?",
  cod="""chmod +x instalar.sh   # da permiso de ejecución
./instalar.sh          # ahora sí se ejecuta""", h="da permiso de ejecución a un script y lo ejecuta",
  pr=("La orden que cambia los permisos de un archivo es ___. (5 letras)", "chmod"),
  pr2=("Para ejecutar una orden como administrador en Linux se antepone ___. (4 letras)", "sudo"),
  ec="usar sudo para todo aunque no haga falta", out="Instalando dependencias..."),
K("Procesos", d="programas que se están ejecutando en el sistema", u="ver qué se está ejecutando y detener lo que se colgó",
  mas="ps lista procesos y top (o htop) los muestra en vivo con su consumo. kill PID termina un proceso por su número. Un & al final de una orden la deja en segundo plano. En PowerShell se usan Get-Process y Stop-Process; en CMD, tasklist y taskkill.",
  k=["Cada proceso tiene un número llamado PID.", "kill termina un proceso usando su PID.", "Un & al final deja la orden en segundo plano."],
  sit="Un servidor quedó abierto ocupando el puerto y quieres terminarlo usando su número de proceso. ¿Qué orden usas?",
  cod="""ps aux | grep node   # busca el proceso de node
kill 4821            # lo termina por su PID""", h="busca un proceso y lo termina",
  pr=("El número que identifica un proceso se llama ___. (3 letras)", "pid"),
  pr2=("En CMD, la orden que termina un proceso es ___. (8 letras)", "taskkill"),
  ec="cerrar la terminal pensando que eso detiene todos los procesos", out="ana  4821  0.3  node server.js"),
K("Scripts de Bash", d="archivos con varias órdenes que se ejecutan juntas", u="automatizar tareas que repites a menudo",
  mas="Un script empieza con #!/bin/bash (shebang) y contiene órdenes, variables, if y for. Se ejecuta con bash script.sh o, si es ejecutable, con ./script.sh. Los argumentos llegan como $1, $2… y $# es cuántos hay.",
  k=["Un script de Bash empieza con la línea #!/bin/bash.", "Los argumentos de un script se leen como $1 y $2.", "Un script automatiza órdenes que se repiten."],
  sit="Todos los días ejecutas las mismas cinco órdenes para preparar tu proyecto y quieres hacerlo con una sola. ¿Qué escribes?",
  cod="""#!/bin/bash
# saludo.sh: saluda a quien le pases
nombre=$1
echo "Hola, $nombre\"""", h="script que saluda al nombre que recibe como argumento",
  pr=("La primera línea #!/bin/bash de un script se llama ___. (7 letras)", "shebang"),
  pr2=("En un script de Bash, el primer argumento se lee con $___. (1 carácter)", "1"),
  ec="olvidar el permiso de ejecución del script", out="Hola, Ana"),
]

E3 = [
K("PowerShell", d="terminal moderna de Windows que trabaja con objetos", u="automatizar Windows y administrar el sistema con scripts",
  mas="PowerShell viene con Windows y también existe para Linux y macOS. Sus órdenes se llaman cmdlets y siguen el formato Verbo-Sustantivo, como Get-ChildItem o Set-Location. Muchas tienen alias conocidos: ls, cd, cat, cp. Sus scripts terminan en .ps1.",
  k=["Las órdenes de PowerShell se llaman cmdlets.", "Los cmdlets siguen el formato Verbo-Sustantivo.", "Los scripts de PowerShell tienen la extensión .ps1."],
  sit="Trabajas en Windows y quieres una terminal con scripts potentes que manejen objetos en lugar de solo texto. ¿Cuál usas?",
  cod="""# PowerShell: lista los archivos .js (alias: ls)
Get-ChildItem -Filter *.js""", h="lista los archivos JavaScript con un cmdlet",
  pr=("Las órdenes de PowerShell se llaman ___. (7 letras)", "cmdlets", "cmdlet"),
  pr2=("La extensión de un script de PowerShell es .___. (3 caracteres)", "ps1"),
  ec="ejecutar un .ps1 descargado sin revisar qué hace", out="main.js\nutils.js"),
K("Get-Help y Get-Command", d="cmdlets para descubrir y aprender otras órdenes", u="encontrar la orden que necesitas sin salir de PowerShell",
  mas="Get-Command *proceso* busca cmdlets por nombre y Get-Help Nombre -Examples muestra ejemplos de uso. Get-Member muestra las propiedades de los objetos que devuelve una orden. En Bash, el equivalente de ayuda es man o la opción --help.",
  k=["Get-Help muestra la ayuda de un cmdlet.", "Get-Command busca cmdlets por su nombre.", "En Bash la ayuda se consulta con man o --help."],
  sit="Quieres ver ejemplos de cómo se usa Get-ChildItem sin buscar en internet. ¿Qué cmdlet usas?",
  cod="""Get-Help Get-ChildItem -Examples   # ejemplos de uso
Get-Command *Process*              # cmdlets sobre procesos""", h="muestra ejemplos de un cmdlet y busca cmdlets por nombre",
  pr=("El cmdlet que muestra la ayuda de otro cmdlet es Get-___. (4 letras)", "help"),
  pr2=("En Bash, la orden que abre el manual de otra orden es ___. (3 letras)", "man"),
  ec="memorizar órdenes en vez de usar la ayuda integrada", out="Get-Process\nStop-Process\nStart-Process"),
K("Pipeline de objetos", d="en PowerShell el pipe pasa objetos con propiedades", u="filtrar y ordenar resultados por sus propiedades",
  mas="Get-Process devuelve objetos con propiedades como Name y CPU. Con el pipe se pueden filtrar (Where-Object), ordenar (Sort-Object) o elegir columnas (Select-Object). No hace falta recortar texto como en Bash: se usan los nombres de las propiedades.",
  k=["Where-Object filtra objetos por una condición.", "Sort-Object ordena objetos por una propiedad.", "Select-Object elige qué propiedades mostrar."],
  sit="En PowerShell quieres ver solo los procesos que más CPU usan, ordenados de mayor a menor. ¿Qué cmdlet ordena?",
  cod="""Get-Process | Sort-Object CPU -Descending | Select-Object -First 3 Name, CPU""", h="muestra los tres procesos que más CPU usan",
  pr=("El cmdlet que filtra objetos por una condición es ___-Object. (5 letras)", "where"),
  pr2=("El cmdlet que ordena objetos es ___-Object. (4 letras)", "sort"),
  ec="tratar la salida de PowerShell como texto plano y cortarla a mano", out="Name     CPU\n----     ---\nchrome   812.4\ncode     301.9\nnode     120.2"),
K("CMD", d="intérprete de comandos clásico de Windows", u="ejecutar órdenes y archivos .bat en cualquier Windows",
  mas="CMD (símbolo del sistema) existe desde hace décadas. Usa dir, cd, copy, move, del, type y cls. Las variables se leen con %NOMBRE% y los scripts son archivos .bat o .cmd. Hoy se prefiere PowerShell, pero muchos tutoriales y herramientas aún usan CMD.",
  k=["CMD usa dir para listar archivos.", "En CMD las variables se leen entre signos de porcentaje.", "Los scripts de CMD son archivos .bat."],
  sit="Un tutorial te pide ejecutar un archivo instalar.bat en Windows. ¿Qué intérprete lo ejecuta?",
  cod="""REM CMD: muestra el usuario y limpia la pantalla
echo Hola %USERNAME%
cls""", h="saluda al usuario de Windows y limpia la pantalla",
  pr=("La extensión de los scripts clásicos de CMD es .___. (3 letras)", "bat", "cmd"),
  pr2=("La orden de CMD que limpia la pantalla es ___. (3 letras)", "cls"),
  ec="escribir sintaxis de Bash, como $VAR, dentro de CMD", out="Hola Ana"),
K("Equivalencias entre terminales", d="la misma tarea se escribe distinto en Bash, PowerShell y CMD", u="seguir tutoriales sin importar tu sistema operativo",
  mas="Listar: ls / Get-ChildItem / dir. Ver archivo: cat / Get-Content / type. Borrar: rm / Remove-Item / del. Limpiar: clear / Clear-Host / cls. Variable: $HOME / $env:USERPROFILE / %USERPROFILE%. En Windows también puedes usar Bash con Git Bash o WSL.",
  k=["Remove-Item es el equivalente de rm en PowerShell.", "Git Bash permite usar Bash en Windows.", "WSL ejecuta Linux real dentro de Windows."],
  sit="Tu tutorial usa órdenes de Linux pero estás en Windows y quieres ejecutarlas tal cual en una terminal Bash. ¿Qué instalas?",
  cod="""# Bash          PowerShell        CMD
# ls            Get-ChildItem     dir
# cat a.txt     Get-Content a.txt type a.txt
# rm a.txt      Remove-Item a.txt del a.txt
clear""", h="compara la misma tarea en las tres terminales",
  pr=("La función de Windows que ejecuta Linux real se llama ___. (3 letras)", "wsl"),
  pr2=("El cmdlet de PowerShell equivalente a cat es Get-___. (7 letras)", "content"),
  ec="copiar órdenes de Linux en CMD esperando que funcionen igual", out=""),
K("Gestores de paquetes", d="herramientas que instalan programas desde la terminal", u="instalar y actualizar software con una sola orden",
  mas="En Linux: apt (Ubuntu, Debian) o dnf. En macOS: Homebrew (brew). En Windows: winget o Chocolatey. Para librerías de código: npm (JavaScript) y pip (Python). Así se instala, actualiza o desinstala sin descargar instaladores a mano.",
  k=["winget instala programas en Windows desde la terminal.", "Homebrew es el gestor de paquetes más usado en macOS.", "apt instala paquetes en Ubuntu y Debian."],
  sit="En Windows quieres instalar Git desde PowerShell con una sola orden, sin descargar un instalador. ¿Qué gestor usas?",
  cod="""winget install Git.Git        # Windows
brew install git              # macOS
sudo apt install git          # Ubuntu""", h="instala Git con el gestor de paquetes de cada sistema",
  pr=("El gestor de paquetes integrado en Windows es ___. (6 letras)", "winget"),
  pr2=("En macOS, el gestor de paquetes más usado es ___. (4 letras)", "brew", "homebrew"),
  ec="instalar programas descargando ejecutables de sitios no oficiales", out="Instalado correctamente: Git"),
K("SSH", d="protocolo para abrir una terminal segura en otro computador", u="administrar servidores remotos y conectarte a GitHub sin contraseña",
  mas="ssh usuario@servidor abre una terminal en esa máquina por un canal cifrado. Con ssh-keygen se crea un par de claves: la pública se copia al servidor (o a GitHub) y la privada nunca se comparte. scp copia archivos por SSH.",
  k=["SSH abre una terminal remota cifrada.", "ssh-keygen crea un par de claves pública y privada.", "La clave privada de SSH nunca se comparte."],
  sit="Necesitas entrar a la terminal de tu servidor en la nube de forma segura desde tu computador. ¿Qué usas?",
  cod="""ssh-keygen -t ed25519 -C "ana@correo.com"   # crea las claves
ssh ana@mi-servidor.com                      # entra al servidor""", h="crea claves SSH y abre una sesión remota",
  pr=("La orden que crea un par de claves SSH es ssh-___. (6 letras)", "keygen"),
  pr2=("De las dos claves SSH, la que nunca se comparte es la ___. (7 letras)", "privada"),
  ec="subir o enviar la clave privada en lugar de la pública", out="ana@mi-servidor:~$"),
K("Terminal en VS Code", d="terminal integrada dentro del editor", u="ejecutar órdenes del proyecto sin cambiar de ventana",
  mas="En VS Code se abre con Ctrl+` (y en CódigoCamp con el botón Terminal). Puedes tener varias terminales, elegir Bash, PowerShell o CMD como predeterminada y dividir la pantalla. La terminal arranca en la carpeta del proyecto abierto.",
  k=["Ctrl+` abre la terminal integrada de VS Code.", "La terminal de VS Code empieza en la carpeta del proyecto.", "VS Code permite elegir Bash, PowerShell o CMD."],
  sit="Estás programando en el editor y quieres ejecutar npm run dev sin abrir otra ventana. ¿Qué atajo usas?",
  cod="""# En la terminal integrada (Ctrl+`):
npm run dev""", h="ejecuta el servidor de desarrollo desde la terminal del editor",
  pr=("El atajo para abrir la terminal integrada en VS Code es Ctrl+___. (1 carácter)", "`"),
  pr2=("La terminal integrada empieza en la carpeta del ___. (8 letras)", "proyecto"),
  ec="ejecutar órdenes del proyecto desde una carpeta distinta", out="VITE ready in 312 ms\n➜ Local: http://localhost:5173/"),
]

ETAPAS_CONCEPTOS = [
    ("Primeros pasos en la terminal", "Navega, crea y organiza archivos con órdenes", E1),
    ("La terminal como herramienta", "Rutas, pipes, búsquedas, variables, permisos y scripts", E2),
    ("PowerShell, CMD y más", "Las terminales de Windows, paquetes, SSH y VS Code", E3),
    ("Automatiza con scripts", "Bash y PowerShell: argumentos, if, bucles, funciones y cron", E4),
    ("Terminal profesional", "find, sed, awk, curl, WSL, alias y tmux", E5),
]
