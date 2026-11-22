"""Git y GitHub: control de versiones, ramas y trabajo en equipo. 3 etapas."""
from ..generador import K
from .git_e45 import E4, E5
from .git_e678 import E6, E7, E8

E1 = [
K("Qué es Git", d="sistema de control de versiones que guarda el historial de un proyecto", u="volver a versiones anteriores y saber quién cambió qué",
  mas="Git toma «fotos» del proyecto llamadas commits. Cada commit guarda qué cambió, quién lo hizo y cuándo, así puedes comparar, deshacer o recuperar cualquier versión. Funciona en tu computador, sin internet; GitHub es un servicio aparte para compartir repositorios.",
  k=["Git guarda el historial de cambios de un proyecto.", "Git funciona en tu computador aunque no haya internet.", "Con Git puedes volver a cualquier versión guardada."],
  sit="Rompiste tu proyecto y quieres volver a como estaba ayer, sabiendo exactamente qué cambiaste. ¿Qué herramienta usas?",
  cod="""git --version   # comprueba que Git está instalado""", h="muestra la versión instalada de Git",
  pr=("El sistema de control de versiones más usado del mundo es ___. (3 letras)", "git"),
  pr2=("Cada foto del proyecto que guarda Git se llama ___. (6 letras)", "commit"),
  ec="confundir Git, la herramienta, con GitHub, el servicio en internet", out="git version 2.45.0"),
K("git init", d="orden que convierte una carpeta en un repositorio de Git", u="empezar a versionar un proyecto nuevo",
  mas="git init crea una carpeta oculta .git donde Git guarda todo el historial. Solo se hace una vez por proyecto. A partir de ahí, Git vigila los archivos de esa carpeta y sus subcarpetas.",
  k=["git init crea un repositorio nuevo.", "El historial se guarda en la carpeta oculta .git.", "git init se ejecuta una sola vez por proyecto."],
  sit="Empezaste un proyecto nuevo en una carpeta vacía y quieres que Git comience a guardar su historial. ¿Qué orden usas?",
  cod="""mkdir mi-app && cd mi-app
git init""", h="crea una carpeta y la convierte en repositorio",
  pr=("La orden que crea un repositorio nuevo es git ___. (4 letras)", "init"),
  pr2=("Git guarda el historial en la carpeta oculta ___. (4 caracteres)", ".git"),
  ec="borrar la carpeta .git y perder todo el historial", out="Initialized empty Git repository in /home/ana/mi-app/.git/"),
K("git status", d="orden que muestra el estado de los archivos del repositorio", u="saber qué cambió y qué está listo para el próximo commit",
  mas="git status dice en qué rama estás, qué archivos cambiaron, cuáles están preparados (staged) y cuáles Git todavía no sigue (untracked). Es la orden que más vas a usar: ejecútala antes y después de cada paso.",
  k=["git status muestra qué archivos cambiaron.", "Los archivos untracked son los que Git aún no sigue.", "git status también dice en qué rama estás."],
  sit="Antes de guardar tu trabajo quieres ver qué archivos modificaste y cuáles todavía no sigue Git. ¿Qué orden usas?",
  cod="""git status""", h="muestra la rama y el estado de los archivos",
  pr=("La orden que muestra el estado de los archivos es git ___. (6 letras)", "status"),
  pr2=("Un archivo que Git todavía no sigue está ___. (9 letras, en inglés)", "untracked"),
  ec="hacer commit sin revisar antes git status", out="On branch main\nUntracked files:\n\tindex.html"),
K("git add", d="orden que prepara cambios para el próximo commit", u="elegir exactamente qué cambios entran en cada commit",
  mas="Git tiene un área de preparación (staging area). git add archivo pone ese cambio en ella y git add . prepara todo. Así puedes hacer commits pequeños y ordenados, aunque hayas cambiado muchos archivos a la vez.",
  k=["git add pone cambios en el área de preparación.", "git add . prepara todos los cambios de la carpeta.", "Solo lo preparado entra en el próximo commit."],
  sit="Cambiaste tres archivos pero solo quieres guardar en el próximo commit los cambios de index.html. ¿Qué orden usas?",
  cod="""git add index.html   # prepara solo este archivo
git status""", h="prepara un archivo para el próximo commit",
  pr=("La orden que prepara cambios para el commit es git ___. (3 letras)", "add"),
  pr2=("El área donde esperan los cambios preparados se llama staging ___. (4 letras)", "area"),
  ec="usar git add . sin revisar y subir archivos que no querías", out="Changes to be committed:\n\tnew file:   index.html"),
K("git commit", d="orden que guarda los cambios preparados en el historial", u="crear un punto del historial al que puedes volver",
  mas="git commit -m \"mensaje\" guarda lo preparado con una descripción. Un buen mensaje dice qué cambió en presente: «Agrega formulario de contacto». Antes del primer commit hay que configurar tu nombre y correo con git config.",
  k=["git commit guarda lo preparado en el historial.", "Cada commit lleva un mensaje que describe el cambio.", "git config define el nombre y el correo del autor."],
  sit="Ya preparaste los cambios del formulario y quieres guardarlos en el historial con una descripción. ¿Qué orden usas?",
  cod="""git config --global user.name "Ana Pérez"
git commit -m "Agrega formulario de contacto\"""", h="configura el autor y guarda un commit con mensaje",
  pr=("La opción de git commit para escribir el mensaje es -___. (1 letra)", "m"),
  pr2=("El nombre del autor se configura con git ___ user.name. (6 letras)", "config"),
  ec="escribir mensajes como «cambios» que no explican nada", out="[main 3f2a1c9] Agrega formulario de contacto\n 1 file changed, 24 insertions(+)"),
K("git log", d="orden que muestra el historial de commits", u="revisar qué se hizo, cuándo y quién",
  mas="git log lista los commits del más nuevo al más viejo con su autor, fecha y mensaje. git log --oneline los resume en una línea y --graph dibuja las ramas. Cada commit tiene un identificador (hash) como 3f2a1c9.",
  k=["git log muestra los commits del más nuevo al más viejo.", "git log --oneline resume cada commit en una línea.", "Cada commit tiene un identificador llamado hash."],
  sit="Quieres ver la lista de commits del proyecto, uno por línea, para encontrar uno de la semana pasada. ¿Qué orden usas?",
  cod="""git log --oneline""", h="lista el historial en forma resumida",
  pr=("La opción de git log que muestra un commit por línea es --___. (7 letras)", "oneline"),
  pr2=("El identificador único de cada commit se llama ___. (4 letras)", "hash"),
  ec="buscar cambios viejos a mano en vez de revisar el historial", out="3f2a1c9 Agrega formulario de contacto\n8b0d4e2 Primer commit"),
K(".gitignore", d="archivo que lista lo que Git no debe seguir", u="dejar fuera dependencias, compilados y secretos",
  mas="Cada línea de .gitignore es un patrón: node_modules/, .env, *.log, dist/. Git ignora esos archivos y no aparecen en git status. Es clave para no subir contraseñas ni carpetas enormes que se pueden volver a instalar.",
  k=["Lo que está en .gitignore no aparece en git status.", ".gitignore evita subir carpetas como node_modules.", "El archivo .env con secretos debe ir en .gitignore."],
  sit="No quieres que la carpeta node_modules ni el archivo .env con tus claves se guarden en el repositorio. ¿Qué archivo creas?",
  cod="""# .gitignore
node_modules/
.env
*.log""", h="ignora dependencias, el archivo de secretos y los logs",
  pr=("El archivo que lista lo que Git debe ignorar es ___. (10 caracteres)", ".gitignore"),
  pr2=("En .gitignore, el patrón *.log ignora todos los archivos .___. (3 letras)", "log"),
  ec="crear .gitignore después de subir los secretos a GitHub", out=""),
K("git diff", d="orden que muestra las diferencias línea por línea", u="revisar exactamente qué cambiaste antes de hacer commit",
  mas="git diff compara tus archivos con el último commit; las líneas con + se agregaron y las con - se quitaron. git diff --staged muestra lo que ya preparaste. En VS Code y en CódigoCamp también puedes verlo en el panel de control de código fuente.",
  k=["git diff muestra lo que cambió línea por línea.", "En git diff, las líneas con + son las agregadas.", "git diff --staged muestra los cambios ya preparados."],
  sit="Antes de hacer commit quieres ver línea por línea qué cambiaste en estilos.css. ¿Qué orden usas?",
  cod="""git diff estilos.css""", h="muestra las líneas cambiadas de un archivo",
  pr=("La orden que muestra las diferencias línea por línea es git ___. (4 letras)", "diff"),
  pr2=("En git diff, las líneas eliminadas empiezan con el signo ___. (1 carácter)", "-"),
  ec="hacer commit sin revisar qué cambió de verdad", out="-  color: red;\n+  color: blue;"),
]

E2 = [
K("Ramas", d="líneas de trabajo independientes dentro del mismo repositorio", u="probar ideas o crear funciones sin romper la versión principal",
  mas="La rama principal suele llamarse main. git branch nueva crea una rama y git switch nueva se cambia a ella (git switch -c hace las dos cosas). Los commits en una rama no afectan a las demás hasta que se unen.",
  k=["La rama principal suele llamarse main.", "git switch -c crea una rama y se cambia a ella.", "Los commits de una rama no afectan a las otras."],
  sit="Quieres crear una función nueva sin tocar la versión que ya funciona en main. ¿Qué creas?",
  cod="""git switch -c login   # crea la rama login y entra
git branch            # lista las ramas""", h="crea una rama nueva y lista las ramas",
  pr=("La orden moderna para cambiar de rama es git ___. (6 letras)", "switch", "checkout"),
  pr2=("La rama principal de un repositorio suele llamarse ___. (4 letras)", "main", "master"),
  ec="trabajar siempre en main y romper la versión estable", out="* login\n  main"),
K("git merge", d="orden que une los cambios de una rama en otra", u="incorporar una función terminada a la rama principal",
  mas="Te cambias a la rama que recibe los cambios (main) y ejecutas git merge rama. Si nadie más cambió main, es un fast-forward; si ambas cambiaron, Git crea un commit de merge. Después puedes borrar la rama con git branch -d.",
  k=["git merge une otra rama en la rama actual.", "Primero te cambias a la rama que recibe los cambios.", "git branch -d borra una rama ya unida."],
  sit="Terminaste la función en la rama login y quieres llevar esos cambios a main. ¿Qué orden usas?",
  cod="""git switch main
git merge login
git branch -d login""", h="une la rama login en main y luego la borra",
  pr=("La orden que une una rama en la actual es git ___. (5 letras)", "merge"),
  pr2=("Cuando main no cambió, el merge es un fast-___. (7 letras)", "forward"),
  ec="hacer merge desde la rama equivocada", out="Updating 8b0d4e2..3f2a1c9\nFast-forward"),
K("Conflictos de merge", d="cambios incompatibles en las mismas líneas de dos ramas", u="decidir a mano qué versión queda cuando Git no puede elegir",
  mas="Git marca el conflicto dentro del archivo con <<<<<<<, ======= y >>>>>>>. Eliges qué queda (una versión, la otra o una mezcla), borras las marcas, haces git add del archivo y git commit. Si te arrepientes, git merge --abort deshace el merge.",
  k=["Un conflicto aparece cuando dos ramas cambian las mismas líneas.", "Git marca los conflictos con <<<<<<< y >>>>>>>.", "git merge --abort cancela un merge con conflictos."],
  sit="Al unir dos ramas, Git dice que no puede combinar automáticamente index.html porque ambos cambiaron la misma línea. ¿Qué pasó?",
  cod="""<<<<<<< HEAD
<h1>Bienvenido</h1>
=======
<h1>Hola</h1>
>>>>>>> otra-rama""", h="muestra cómo marca Git un conflicto en un archivo",
  pr=("Para cancelar un merge con conflictos usas git merge --___. (5 letras)", "abort"),
  pr2=("Después de resolver un conflicto, el archivo se prepara con git ___. (3 letras)", "add"),
  ec="hacer commit dejando las marcas <<<<<<< dentro del archivo", out=""),
K("Deshacer cambios", d="órdenes para descartar o revertir cambios", u="arreglar errores sin perder el historial",
  mas="git restore archivo descarta cambios sin guardar; git restore --staged lo saca de la preparación. git revert commit crea un commit nuevo que deshace otro (seguro en ramas compartidas). git reset --hard mueve la rama atrás y borra cambios: úsalo con cuidado.",
  k=["git restore descarta cambios que no guardaste.", "git revert deshace un commit creando otro nuevo.", "git reset --hard borra cambios sin preguntar."],
  sit="Subiste un commit con un error a la rama compartida y quieres deshacerlo sin reescribir el historial de nadie. ¿Qué orden usas?",
  cod="""git restore estilos.css      # descarta cambios locales
git revert 3f2a1c9           # deshace un commit con otro nuevo""", h="descarta cambios locales y revierte un commit",
  pr=("La orden que deshace un commit creando uno nuevo es git ___. (6 letras)", "revert"),
  pr2=("Para descartar cambios no guardados de un archivo usas git ___. (7 letras)", "restore"),
  ec="usar reset --hard en una rama compartida y borrar trabajo ajeno", out="[main 9c1e0aa] Revert \"Agrega formulario\""),
K("git stash", d="orden que guarda cambios a medias para después", u="cambiar de rama sin hacer commit de algo incompleto",
  mas="git stash guarda tus cambios sin commit y deja el árbol limpio. Te cambias de rama, haces lo urgente, vuelves y git stash pop recupera lo guardado. git stash list muestra lo que tienes guardado.",
  k=["git stash guarda cambios sin hacer commit.", "git stash pop recupera lo guardado.", "git stash list muestra los cambios guardados."],
  sit="Estás a mitad de un cambio y te piden arreglar algo urgente en otra rama, sin hacer commit de lo incompleto. ¿Qué usas?",
  cod="""git stash        # guarda lo que tenías a medias
git switch main  # haces lo urgente…
git switch login
git stash pop    # recuperas tu trabajo""", h="guarda cambios a medias y los recupera después",
  pr=("La orden que recupera lo guardado con stash es git stash ___. (3 letras)", "pop"),
  pr2=("Para ver lo que tienes guardado usas git stash ___. (4 letras)", "list"),
  ec="olvidar hacer stash pop y creer que perdiste el trabajo", out="Saved working directory and index state WIP on login"),
K("Etiquetas", d="nombres fijos para marcar versiones importantes", u="identificar lanzamientos como v1.0 en el historial",
  mas="git tag v1.0 pone una etiqueta en el commit actual; con -a y -m es una etiqueta anotada con mensaje. Las etiquetas no se mueven como las ramas. En GitHub, las etiquetas sirven para publicar Releases.",
  k=["Una etiqueta marca un commit importante.", "Las etiquetas no se mueven como las ramas.", "GitHub usa etiquetas para publicar Releases."],
  sit="Terminaste la primera versión estable y quieres marcarla en el historial como v1.0. ¿Qué usas?",
  cod="""git tag -a v1.0 -m "Primera versión"
git tag""", h="crea una etiqueta anotada y lista las etiquetas",
  pr=("La orden que crea etiquetas de versión es git ___. (3 letras)", "tag"),
  pr2=("En GitHub, las etiquetas sirven para publicar ___. (8 letras)", "releases", "release"),
  ec="usar ramas para marcar versiones en lugar de etiquetas", out="v1.0"),
]

E3 = [
K("GitHub", d="servicio en internet para guardar y compartir repositorios de Git", u="respaldar tu código, mostrar tu portafolio y colaborar",
  mas="GitHub aloja repositorios remotos y agrega herramientas: issues, pull requests, Actions, Pages. Un repositorio puede ser público o privado. GitLab y Bitbucket son alternativas parecidas.",
  k=["GitHub guarda repositorios de Git en internet.", "Un repositorio de GitHub puede ser público o privado.", "GitLab y Bitbucket son alternativas a GitHub."],
  sit="Quieres respaldar tu proyecto en internet y que otras personas puedan ver tu código como portafolio. ¿Qué servicio usas?",
  cod="""# En github.com/new creas el repositorio vacío y luego:
git remote add origin https://github.com/ana/mi-app.git""", h="conecta tu repositorio local con uno de GitHub",
  pr=("El servicio más usado para alojar repositorios de Git es ___. (6 letras)", "github"),
  pr2=("Un repositorio que todos pueden ver es ___. (7 letras)", "público", "publico"),
  ec="pensar que GitHub es obligatorio para usar Git", out=""),
K("Remotos", d="copias del repositorio en otro lugar, como GitHub", u="sincronizar tu trabajo local con el de internet",
  mas="git remote add origin URL agrega un remoto llamado origin. git remote -v lista los remotos. Las ramas del remoto se ven como origin/main. Puedes tener varios remotos, por ejemplo origin (tu copia) y upstream (el original).",
  k=["origin es el nombre habitual del remoto principal.", "git remote -v lista los remotos y sus URL.", "Las ramas remotas se ven como origin/main."],
  sit="Creaste un repositorio vacío en GitHub y quieres conectar tu proyecto local con él. ¿Qué agregas?",
  cod="""git remote add origin https://github.com/ana/mi-app.git
git remote -v""", h="agrega el remoto origin y lo lista",
  pr=("El nombre habitual del remoto principal es ___. (6 letras)", "origin"),
  pr2=("Para listar los remotos con su URL usas git remote -___. (1 letra)", "v"),
  ec="escribir mal la URL del remoto y no poder subir", out="origin\thttps://github.com/ana/mi-app.git (fetch)\norigin\thttps://github.com/ana/mi-app.git (push)"),
K("git push", d="orden que sube tus commits al repositorio remoto", u="publicar tu trabajo en GitHub",
  mas="git push -u origin main sube la rama main y la deja enlazada; después basta con git push. Si el remoto tiene commits que tú no tienes, el push se rechaza: primero haces git pull. GitHub pide autenticación con un token o una clave SSH.",
  k=["git push sube los commits al remoto.", "La opción -u enlaza la rama local con la remota.", "Si el remoto tiene cambios nuevos, primero haces pull."],
  sit="Hiciste varios commits en tu computador y quieres que aparezcan en GitHub. ¿Qué orden usas?",
  cod="""git push -u origin main   # la primera vez
git push                  # las siguientes""", h="sube la rama main a GitHub y la enlaza",
  pr=("La orden que sube los commits al remoto es git ___. (4 letras)", "push"),
  pr2=("Para enlazar la rama la primera vez usas git push -___ origin main. (1 letra)", "u"),
  ec="intentar push sin hacer pull cuando el remoto tiene cambios", out="To https://github.com/ana/mi-app.git\n * [new branch]      main -> main"),
K("git clone y git pull", d="órdenes para descargar un repositorio y traer sus novedades", u="trabajar con proyectos que están en GitHub",
  mas="git clone URL descarga el repositorio completo, con todo su historial, en una carpeta nueva. git pull trae los commits nuevos del remoto y los une a tu rama (es fetch más merge). Haz pull antes de empezar a trabajar cada día.",
  k=["git clone descarga un repositorio con todo su historial.", "git pull trae y une los cambios del remoto.", "git pull equivale a git fetch más git merge."],
  sit="Un compañero subió cambios a GitHub y quieres traerlos a tu copia local antes de seguir. ¿Qué orden usas?",
  cod="""git clone https://github.com/ana/mi-app.git
cd mi-app
git pull""", h="descarga un repositorio y trae sus últimas novedades",
  pr=("La orden que descarga un repositorio completo es git ___. (5 letras)", "clone"),
  pr2=("git pull equivale a git fetch más git ___. (5 letras)", "merge"),
  ec="empezar a trabajar sin hacer pull y crear conflictos innecesarios", out="Cloning into 'mi-app'...\nAlready up to date."),
K("Pull requests", d="propuesta para unir los cambios de una rama en GitHub", u="revisar el código en equipo antes de unirlo a main",
  mas="Subes tu rama, abres un pull request (PR) en GitHub y tus compañeros comentan, piden cambios y aprueban. Al final se hace merge desde la web. Así nada llega a main sin revisión.",
  k=["Un pull request propone unir una rama en otra.", "En un pull request el equipo revisa y comenta el código.", "Un pull request se une desde GitHub cuando lo aprueban."],
  sit="Terminaste tu rama y quieres que tu equipo revise el código en GitHub antes de unirlo a main. ¿Qué abres?",
  cod="""git push -u origin login
# En GitHub: «Compare & pull request» → describe el cambio → Create pull request""", h="sube una rama y abre una propuesta de cambio",
  pr=("La propuesta de unir cambios en GitHub se llama pull ___. (7 letras)", "request"),
  pr2=("Las siglas de pull request son ___. (2 letras)", "pr"),
  ec="unir a main sin que nadie revise el código", out=""),
K("Forks", d="copia de un repositorio ajeno en tu cuenta de GitHub", u="contribuir a proyectos de otras personas",
  mas="Un fork crea tu propia copia del repositorio en GitHub. Lo clonas, creas una rama, haces cambios, los subes a tu fork y abres un pull request hacia el original. Así se contribuye al software libre.",
  k=["Un fork es tu copia de un repositorio ajeno.", "Desde un fork se abre un pull request al original.", "Los forks permiten contribuir al software libre."],
  sit="Quieres corregir un error en un proyecto de código abierto donde no tienes permiso de escritura. ¿Qué haces primero en GitHub?",
  cod="""# 1. Botón «Fork» en GitHub
git clone https://github.com/ana/proyecto-libre.git
git switch -c corrige-error""", h="clona tu fork y crea una rama para el arreglo",
  pr=("La copia de un repositorio ajeno en tu cuenta se llama ___. (4 letras)", "fork"),
  pr2=("Para proponer tu arreglo al original abres un pull ___. (7 letras)", "request"),
  ec="intentar hacer push directo a un repositorio sin permiso", out="Cloning into 'proyecto-libre'..."),
K("GitHub Pages y Actions", d="servicios de GitHub para publicar páginas y automatizar tareas", u="publicar tu web gratis y ejecutar pruebas en cada push",
  mas="GitHub Pages publica un sitio estático desde una rama (como main o gh-pages) en usuario.github.io. GitHub Actions ejecuta flujos definidos en .github/workflows/*.yml: pruebas, compilaciones o despliegues automáticos cuando haces push.",
  k=["GitHub Pages publica sitios estáticos gratis.", "Los flujos de GitHub Actions se definen en archivos .yml.", "Actions puede ejecutar pruebas en cada push."],
  sit="Quieres que tu página HTML del portafolio quede publicada en internet gratis desde tu repositorio. ¿Qué usas?",
  cod="""# .github/workflows/pruebas.yml
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm test""", h="ejecuta las pruebas automáticamente en cada push",
  pr=("El servicio de GitHub que publica páginas estáticas es GitHub ___. (5 letras)", "pages"),
  pr2=("Los flujos de GitHub Actions se escriben en archivos .___. (3 letras)", "yml", "yaml"),
  ec="publicar en Pages un proyecto que necesita servidor", out=""),
K("Tokens y SSH en GitHub", d="formas seguras de autenticarte en GitHub desde la terminal", u="hacer push sin escribir tu contraseña",
  mas="GitHub ya no acepta la contraseña en git push. Usa un token personal (Settings → Developer settings → Personal access tokens) o una clave SSH agregada en Settings → SSH keys. Nunca subas tokens al repositorio.",
  k=["GitHub no acepta la contraseña de la cuenta en git push.", "Un token personal reemplaza la contraseña en HTTPS.", "Las claves SSH se agregan en la configuración de GitHub."],
  sit="Al hacer git push, GitHub rechaza tu contraseña normal. ¿Qué creas en la configuración de GitHub para autenticarte?",
  cod="""# Con SSH: copia tu clave pública y agrégala en GitHub
cat ~/.ssh/id_ed25519.pub
git remote set-url origin git@github.com:ana/mi-app.git""", h="usa una clave SSH para autenticarte en GitHub",
  pr=("En lugar de la contraseña, GitHub acepta un ___ personal. (5 letras)", "token"),
  pr2=("Una alternativa al token es una clave ___. (3 letras)", "ssh"),
  ec="pegar un token dentro del código y subirlo a GitHub", out="ssh-ed25519 AAAAC3Nza... ana@correo.com"),
]

ETAPAS_CONCEPTOS = [
    ("Git desde cero", "Repositorios, commits e historial", E1),
    ("Ramas y deshacer", "Trabaja en paralelo, une ramas y corrige errores", E2),
    ("GitHub y equipo", "Remotos, push, pull requests, forks y publicación", E3),
    ("Git avanzado", "Rebase, cherry-pick, reflog, bisect, blame, hooks y submódulos", E4),
    ("Flujos profesionales", "Git Flow, trunk-based, commits convencionales, versiones y revisión", E5),
    ("Git en el día a día", "Configuración, historial, deshacer, remotos y finales de línea", E6),
    ("Git por dentro", "Objetos, HEAD, merges, conflictos, parches y repositorios grandes", E7),
    ("Git profesional", "Firmas, hooks del equipo, changelog, hotfix, secretos y buenas prácticas", E8),
]
