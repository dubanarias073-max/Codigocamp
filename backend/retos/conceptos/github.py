"""GitHub: de crear tu cuenta a Actions, Pages, seguridad y open source. 5 etapas."""
from ..generador import K
from .github_e678 import E6, E7, E8

E1 = [
K("Qué es GitHub", d="plataforma en la nube para guardar repositorios de Git y colaborar", u="tener tu código en línea, trabajar en equipo y mostrar tu portafolio",
  mas="GitHub guarda repositorios de Git en internet y agrega herramientas: issues, pull requests, Actions y Pages. Git es la herramienta que usas en tu computador; GitHub es el sitio donde se comparte. Alternativas: GitLab y Bitbucket.",
  k=["GitHub guarda repositorios de Git en la nube.", "Git funciona en tu computador y GitHub en internet.", "GitLab y Bitbucket son alternativas a GitHub."],
  sit="Quieres guardar tu proyecto en internet, que tu equipo trabaje en él y que las empresas vean tu código. ¿Qué plataforma usas?",
  cod="""git remote add origin https://github.com/ana/tienda.git
git push -u origin main""", h="sube un repositorio local a GitHub",
  pr=("La plataforma más usada para alojar repositorios de Git es ___. (6 letras)", "github"),
  pr2=("Una alternativa a GitHub es Git___. (3 letras)", "lab"),
  ec="creer que Git y GitHub son lo mismo", out="branch 'main' set up to track 'origin/main'."),
K("Repositorio en GitHub", d="proyecto alojado en GitHub con su código, historial y configuración", u="tener un lugar para cada proyecto, público o privado",
  mas="Con el botón New eliges nombre, si es público o privado y si agregas README, .gitignore y licencia. La dirección queda github.com/usuario/repositorio. Los repositorios privados solo los ven las personas que invites.",
  k=["Un repositorio puede ser público o privado.", "La URL de un repositorio es github.com/usuario/nombre.", "Al crear un repositorio puedes agregar README y licencia."],
  sit="Empiezas un proyecto nuevo y quieres que solo tú y tu profesor puedan ver el código en GitHub. ¿Qué tipo de repositorio creas?",
  cod="""gh repo create tienda --private --clone""", h="crea un repositorio privado y lo clona",
  pr=("Un repositorio que solo ven las personas invitadas es ___. (7 letras)", "privado"),
  pr2=("Un repositorio que todos pueden ver es ___. (7 letras)", "publico", "público"),
  ec="subir claves a un repositorio público", out="✓ Created repository ana/tienda on GitHub"),
K("README y Markdown", d="archivo de portada del repositorio escrito en Markdown", u="explicar qué hace el proyecto y cómo usarlo",
  mas="GitHub muestra README.md en la página principal del repositorio. Markdown usa # para títulos, **negrita**, - para listas, [texto](url) para enlaces y ``` para bloques de código. Un buen README dice qué es, cómo instalarlo y cómo usarlo.",
  k=["GitHub muestra README.md en la portada del repositorio.", "En Markdown, # crea un título.", "Un README explica cómo instalar y usar el proyecto."],
  sit="Cualquiera que entra a tu repositorio no entiende qué hace ni cómo ejecutarlo. ¿Qué archivo agregas?",
  cod="""# Tienda
App para vender productos.

## Cómo iniciarla
```
npm install
npm run dev
```""", h="un README con título, descripción e instrucciones",
  pr=("El archivo de portada de un repositorio es README.___. (2 letras)", "md"),
  pr2=("En Markdown, el símbolo de título es ___. (1 carácter)", "#"),
  ec="dejar el README vacío o solo con el nombre del proyecto", out=""),
K("Licencias", d="texto que dice qué pueden hacer otros con tu código", u="permitir o limitar que otros usen, cambien o vendan tu proyecto",
  mas="Sin licencia, nadie puede reutilizar legalmente tu código aunque sea público. MIT permite casi todo con atribución; GPL obliga a que los derivados también sean libres; Apache 2.0 agrega protección de patentes. Se guarda en el archivo LICENSE.",
  k=["Sin licencia nadie puede reutilizar legalmente tu código.", "MIT es una licencia muy permisiva.", "La licencia se guarda en el archivo LICENSE."],
  sit="Publicaste una librería y quieres que cualquiera la use, incluso en proyectos comerciales, solo dándote crédito. ¿Qué licencia eliges?",
  cod="""MIT License

Copyright (c) 2026 Ana""", h="comienzo del archivo LICENSE con licencia MIT",
  pr=("La licencia permisiva más usada es ___. (3 letras)", "mit"),
  pr2=("La licencia se guarda en el archivo ___. (7 letras)", "license"),
  ec="copiar código de un repositorio sin licencia y usarlo como propio", out=""),
K("Subir archivos desde la web", d="agregar o editar archivos directamente en github.com", u="hacer cambios pequeños sin usar la terminal",
  mas="En el repositorio, Add file → Upload files sube archivos arrastrándolos y el lápiz edita uno. Cada cambio pide un mensaje y crea un commit. Para trabajo diario es mejor clonar y usar Git o VS Code.",
  k=["En la web, cada cambio crea un commit.", "Upload files sube archivos arrastrándolos.", "El ícono del lápiz edita un archivo en GitHub."],
  sit="Necesitas corregir un error de ortografía en el README desde el celular, sin Git instalado. ¿Qué usas?",
  cod="""# En github.com: abre README.md → ícono del lápiz → edita
# → Commit changes… → mensaje: "Corrige ortografía\"""", h="pasos para editar un archivo desde la web",
  pr=("En la web de GitHub, cada cambio guardado crea un ___. (6 letras)", "commit"),
  pr2=("El botón que sube archivos se llama Upload ___. (5 letras)", "files"),
  ec="editar en la web y olvidar hacer pull antes de seguir en tu computador", out=""),
K("Clonar con HTTPS", d="descargar un repositorio de GitHub con su historial usando la URL https", u="trabajar en tu computador en un proyecto que está en GitHub",
  mas="El botón verde Code muestra la URL; git clone URL crea la carpeta con todo el historial. Para hacer push por HTTPS, GitHub pide un token personal (no la contraseña) o usar GitHub CLI o Git Credential Manager.",
  k=["El botón Code muestra la URL para clonar.", "git clone descarga todo el historial.", "Para push por HTTPS se usa un token, no la contraseña."],
  sit="Tu compañero creó el repositorio del proyecto en GitHub y necesitas tenerlo en tu computador. ¿Qué haces?",
  cod="""git clone https://github.com/ana/tienda.git
cd tienda""", h="clona un repositorio y entra en su carpeta",
  pr=("El botón de GitHub con la URL para clonar es el botón ___. (4 letras)", "code"),
  pr2=("Para hacer push por HTTPS GitHub pide un ___. (5 letras)", "token"),
  ec="intentar hacer push con la contraseña de la cuenta", out="Cloning into 'tienda'...\nReceiving objects: 100% (98/98), done."),
K("GitHub Desktop", d="aplicación gráfica oficial para usar Git y GitHub", u="hacer commits, ramas y push con botones en lugar de órdenes",
  mas="GitHub Desktop muestra los cambios, permite escribir el mensaje del commit, cambiar de rama y sincronizar (pull y push) con un botón. VS Code también tiene un panel de Git integrado. Entender las órdenes sigue siendo importante.",
  k=["GitHub Desktop es la aplicación gráfica oficial de GitHub.", "GitHub Desktop sincroniza con un botón.", "VS Code tiene un panel de Git integrado."],
  sit="Tu compañera de diseño quiere subir cambios al repositorio pero no le gusta la terminal. ¿Qué aplicación le recomiendas?",
  cod="""# GitHub Desktop: Changes → escribe el resumen → Commit to main → Push origin""", h="pasos para hacer commit y push con la aplicación",
  pr=("La aplicación gráfica oficial de GitHub es GitHub ___. (7 letras)", "desktop"),
  pr2=("El botón que sube tus commits se llama ___ origin. (4 letras)", "push"),
  ec="hacer commit de todos los archivos sin mirar qué cambió", out=""),
K("Explorar GitHub", d="estrellas, seguimiento, temas y búsqueda de repositorios", u="encontrar proyectos para aprender y seguir los que te interesan",
  mas="Star guarda un repositorio en tus favoritos (y muestra su popularidad), Watch te avisa de su actividad y Topics agrupan por tema. La búsqueda acepta filtros como language:python stars:>1000.",
  k=["Star guarda un repositorio en favoritos.", "Watch avisa de la actividad de un repositorio.", "La búsqueda acepta filtros como language:python."],
  sit="Encontraste un repositorio de ejemplos de FastAPI y quieres guardarlo para volver luego. ¿Qué botón usas?",
  cod="""# En la búsqueda de GitHub:
language:python stars:>1000 fastapi""", h="busca repositorios de Python populares sobre FastAPI",
  pr=("El botón que guarda un repositorio en favoritos es ___. (4 letras)", "star"),
  pr2=("El botón que avisa de la actividad de un repositorio es ___. (5 letras)", "watch"),
  ec="medir la calidad de un proyecto solo por sus estrellas", out=""),
]

E2 = [
K("Issues", d="tarjetas para reportar errores, pedir funciones o anotar tareas", u="organizar el trabajo pendiente de un proyecto",
  mas="Un issue tiene título, descripción, comentarios, etiquetas y responsables. Se cierran solos si un commit o pull request dice «Fixes #12». Las plantillas de issues piden la información necesaria para reportar bien un error.",
  k=["Un issue reporta un error o pide una función.", "«Fixes #12» cierra el issue 12 al unir el cambio.", "Los issues pueden tener etiquetas y responsables."],
  sit="Un usuario encontró un error en tu app y quieres dejarlo registrado para arreglarlo después. ¿Qué creas en GitHub?",
  cod="""gh issue create --title "El botón Pagar no responde" --label bug""", h="crea un issue con la etiqueta bug",
  pr=("En GitHub, un reporte de error o tarea se llama ___. (5 letras)", "issue"),
  pr2=("La palabra que cierra un issue desde un commit es ___ #12. (5 letras)", "fixes"),
  ec="reportar «no funciona» sin pasos para reproducir el error", out="https://github.com/ana/tienda/issues/12"),
K("Etiquetas y responsables", d="formas de clasificar issues y asignar quién los atiende", u="saber de un vistazo qué es urgente y quién se encarga",
  mas="Labels como bug, enhancement o good first issue clasifican; Assignees indica quién trabaja en algo y Milestones agrupa issues de una versión o entrega. good first issue invita a personas nuevas a contribuir.",
  k=["Las labels clasifican los issues.", "Assignees indica quién trabaja en un issue.", "Milestones agrupa issues de una entrega."],
  sit="Tu equipo tiene 40 issues y no se sabe cuáles son errores ni quién se encarga de cada uno. ¿Qué usas para ordenarlos?",
  cod="""gh issue edit 12 --add-label bug --add-assignee ana --milestone "v1.0\"""", h="etiqueta, asigna y agrupa un issue",
  pr=("La etiqueta para invitar a personas nuevas es good first ___. (5 letras)", "issue"),
  pr2=("Lo que agrupa issues de una entrega es un ___. (9 letras)", "milestone"),
  ec="tener issues sin etiqueta ni responsable que nadie atiende", out=""),
K("Pull request en GitHub", d="propuesta para unir los cambios de una rama a otra, con revisión", u="que el equipo revise y discuta los cambios antes de unirlos",
  mas="Subes tu rama, GitHub ofrece Compare & pull request y escribes qué cambia y por qué. Se ven los archivos cambiados, las pruebas y los comentarios. Al final se une con Merge, Squash and merge o Rebase and merge.",
  k=["Un pull request propone unir una rama a otra.", "En un pull request se ven los archivos cambiados.", "Squash and merge une todos los commits en uno."],
  sit="Terminaste la función del carrito en tu rama y quieres que tu equipo la revise antes de unirla a main. ¿Qué abres en GitHub?",
  cod="""git push -u origin carrito
gh pr create --title "Agrega carrito" --body "Cierra #8\"""", h="sube la rama y abre un pull request",
  pr=("La opción que une todos los commits del pull request en uno es ___ and merge. (6 letras)", "squash"),
  pr2=("Las siglas de pull request son ___. (2 letras)", "pr"),
  ec="abrir pull requests sin descripción", out="https://github.com/ana/tienda/pull/9"),
K("Revisar un pull request", d="leer los cambios, comentar líneas y aprobar o pedir cambios", u="mejorar la calidad del código antes de unirlo",
  mas="En Files changed comentas líneas concretas y con Suggest changes propones el código exacto. Al terminar eliges Comment, Approve o Request changes. El autor responde, corrige y la conversación se marca como resuelta.",
  k=["En Files changed se comentan líneas concretas.", "Request changes pide correcciones antes de unir.", "Suggest changes propone el código exacto."],
  sit="Revisas el pull request de un compañero y encontraste un error que debe corregir antes de unirlo. ¿Qué opción eliges al terminar la revisión?",
  cod="""```suggestion
const total = precio * cantidad;
```""", h="una sugerencia de código en un comentario de revisión",
  pr=("La pestaña donde se ven los cambios del PR es Files ___. (7 letras)", "changed"),
  pr2=("La opción que acepta el pull request es ___. (7 letras)", "approve"),
  ec="hacer comentarios vagos como «esto está mal» sin explicar", out=""),
K("Conflictos en GitHub", d="cuando el pull request no se puede unir porque main cambió las mismas líneas", u="resolver choques de cambios antes de unir",
  mas="GitHub avisa «This branch has conflicts». Para conflictos simples, Resolve conflicts abre un editor con las marcas <<<<<<< ======= >>>>>>>. Si son complejos, haces git merge main en tu rama, los resuelves en VS Code y vuelves a hacer push.",
  k=["GitHub avisa cuando un pull request tiene conflictos.", "Resolve conflicts permite arreglarlos en la web.", "Las marcas <<<<<<< y >>>>>>> separan las dos versiones."],
  sit="Tu pull request dice «This branch has conflicts that must be resolved». ¿Qué debes hacer antes de unirlo?",
  cod="""git switch carrito
git merge main
# arregla los archivos en VS Code
git commit -am "Resuelve conflicto con main" && git push""", h="trae main a tu rama, resuelve y sube",
  pr=("El botón de GitHub para arreglar conflictos en la web es Resolve ___. (9 letras)", "conflicts"),
  pr2=("La marca que separa las dos versiones en conflicto es ___. (7 caracteres)", "======="),
  ec="borrar la versión del compañero sin hablar con él", out=""),
K("Colaboradores y permisos", d="personas con acceso a tu repositorio y su nivel de permiso", u="que tu equipo pueda subir cambios a un repositorio",
  mas="En Settings → Collaborators invitas por usuario o correo. En organizaciones hay roles: Read, Triage, Write, Maintain y Admin. Da el permiso mínimo necesario.",
  k=["Los colaboradores se invitan en Settings.", "El rol Write permite subir cambios.", "Conviene dar el permiso mínimo necesario."],
  sit="Tu compañero de proyecto no puede hacer push a tu repositorio y le sale «Permission denied». ¿Qué debes hacer?",
  cod="""gh api repos/ana/tienda/collaborators/luis -X PUT -f permission=push""", h="invita a luis con permiso de escritura",
  pr=("La persona con acceso a tu repositorio es un ___. (11 letras)", "colaborador"),
  pr2=("El rol con control total del repositorio es ___. (5 letras)", "admin"),
  ec="darle permiso Admin a todo el mundo", out=""),
K("Discussions", d="foro dentro del repositorio para preguntas e ideas", u="separar las conversaciones generales de los issues",
  mas="Discussions tiene categorías como Q&A, Ideas y Anuncios; en Q&A se marca la mejor respuesta. Así los issues quedan solo para trabajo concreto. Se activa en Settings → Features.",
  k=["Discussions es un foro dentro del repositorio.", "En Q&A se marca la mejor respuesta.", "Discussions se activa en Settings."],
  sit="Tus usuarios abren issues para hacer preguntas de cómo usar la librería y se llena de ruido. ¿Qué función de GitHub activas?",
  cod="""# Settings → Features → ✓ Discussions
# Categoría «Q&A» → marca «Mark as answer»""", h="activa Discussions y marca una respuesta",
  pr=("El foro integrado en un repositorio se llama ___. (11 letras)", "discussions"),
  pr2=("La categoría de preguntas y respuestas se llama ___. (3 caracteres)", "q&a"),
  ec="dejar preguntas generales mezcladas con los errores", out=""),
K("Plantillas de issues y PR", d="formularios con secciones que se rellenan al abrir un issue o PR", u="recibir reportes completos y descripciones consistentes",
  mas="En .github/ISSUE_TEMPLATE/ creas formularios para errores y peticiones, y .github/pull_request_template.md da el esquema de cada PR. Así nadie olvida los pasos para reproducir ni la lista de verificación.",
  k=["Las plantillas viven en la carpeta .github.", "ISSUE_TEMPLATE guarda formularios de issues.", "pull_request_template.md da el esquema de los PR."],
  sit="Los reportes de errores llegan sin pasos para reproducir ni versión del navegador. ¿Qué agregas al repositorio?",
  cod="""<!-- .github/pull_request_template.md -->
## Qué cambia
## Cómo probarlo
- [ ] Probé en el navegador""", h="plantilla de descripción de pull request",
  pr=("Las plantillas se guardan en la carpeta .___. (6 letras)", "github"),
  pr2=("La carpeta de formularios de issues es ISSUE____. (8 letras)", "template"),
  ec="hacer plantillas tan largas que nadie las llena", out=""),
]

E3 = [
K("CI/CD", d="integración y entrega continuas: probar y publicar automáticamente cada cambio", u="detectar errores pronto y desplegar sin pasos manuales",
  mas="CI (integración continua) ejecuta las pruebas en cada push o pull request. CD (entrega o despliegue continuo) publica automáticamente lo que pasa las pruebas. En GitHub se hace con GitHub Actions.",
  k=["CI ejecuta las pruebas en cada cambio.", "CD publica automáticamente lo que pasa las pruebas.", "GitHub Actions hace CI/CD en GitHub."],
  sit="Tu equipo olvida correr las pruebas antes de unir cambios y se rompe main seguido. ¿Qué práctica lo evita?",
  cod="""# .github/workflows/pruebas.yml
on: [push, pull_request]""", h="un flujo que corre en cada push y pull request",
  pr=("Las siglas de integración y entrega continuas son ci/___. (2 letras)", "cd"),
  pr2=("El servicio de CI/CD de GitHub es GitHub ___. (7 letras)", "actions"),
  ec="unir cambios sin esperar a que terminen las pruebas", out=""),
K("Workflow YAML", d="archivo en .github/workflows que describe una automatización", u="definir cuándo y qué ejecuta GitHub Actions",
  mas="Un workflow tiene name, on (cuándo corre) y jobs (qué hace). Se escribe en YAML: la sangría con espacios importa. En la pestaña Actions del repositorio ves cada ejecución con sus registros.",
  k=["Los workflows viven en .github/workflows.", "La clave on define cuándo corre un workflow.", "En YAML la sangría con espacios es importante."],
  sit="Quieres automatizar las pruebas de tu proyecto en GitHub. ¿En qué carpeta creas el archivo?",
  cod="""name: Pruebas
on: [push]
jobs:
  probar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm test""", h="workflow que instala dependencias y corre las pruebas",
  pr=("Los workflows se guardan en .github/___. (9 letras)", "workflows"),
  pr2=("El formato de los workflows es ___. (4 letras)", "yaml"),
  ec="usar tabulaciones en el YAML y que el workflow no se lea", out=""),
K("Eventos de un workflow", d="lo que dispara un workflow: push, pull_request, schedule, workflow_dispatch", u="ejecutar la automatización en el momento adecuado",
  mas="push corre en cada push (se puede filtrar por branches), pull_request al abrir o actualizar un PR, schedule con sintaxis cron y workflow_dispatch añade un botón para ejecutarlo a mano.",
  k=["push dispara el workflow en cada push.", "schedule ejecuta un workflow con sintaxis cron.", "workflow_dispatch permite ejecutarlo a mano."],
  sit="Quieres poder lanzar el despliegue con un botón desde la pestaña Actions, no en cada push. ¿Qué evento usas?",
  cod="""on:
  push:
    branches: [main]
  schedule:
    - cron: "0 6 * * 1\"""", h="corre en push a main y cada lunes a las 6",
  pr=("El evento que permite ejecutar un workflow a mano es workflow___. (9 caracteres)", "_dispatch"),
  pr2=("El evento para tareas programadas es ___. (8 letras)", "schedule"),
  ec="ejecutar el despliegue en pull requests de cualquier rama", out=""),
K("Jobs y steps", d="tareas de un workflow y los pasos dentro de cada una", u="dividir la automatización en partes que pueden correr en paralelo",
  mas="Cada job corre en una máquina nueva (runs-on). Sus steps son acciones (uses) u órdenes (run) en orden. Los jobs corren en paralelo, salvo que uno dependa de otro con needs.",
  k=["Cada job corre en una máquina nueva.", "Los steps se ejecutan en orden.", "needs hace que un job espere a otro."],
  sit="Tu workflow tiene un job de pruebas y otro de despliegue; el despliegue solo debe correr si las pruebas pasaron. ¿Qué clave usas?",
  cod="""jobs:
  probar: { runs-on: ubuntu-latest, steps: [{ run: npm test }] }
  desplegar:
    needs: probar
    runs-on: ubuntu-latest
    steps: [{ run: ./desplegar.sh }]""", h="el despliegue espera a las pruebas",
  pr=("La clave que hace que un job espere a otro es ___. (5 letras)", "needs"),
  pr2=("La clave que elige la máquina del job es runs-___. (2 letras)", "on"),
  ec="poner todo en un solo job enorme", out=""),
K("Acciones del Marketplace", d="pasos reutilizables que otros publicaron para GitHub Actions", u="no escribir desde cero tareas comunes",
  mas="actions/checkout descarga tu código, actions/setup-node y actions/setup-python instalan la versión que pides y actions/cache acelera las dependencias. Fija la versión (@v4) y revisa quién publica cada acción.",
  k=["actions/checkout descarga el código del repositorio.", "setup-node instala una versión de Node.", "Conviene fijar la versión de cada acción."],
  sit="Tu workflow necesita Python 3.12 instalado antes de correr las pruebas. ¿Qué acción usas?",
  cod="""- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
- run: pip install -r requirements.txt && pytest""", h="instala Python 3.12 y corre las pruebas",
  pr=("La acción que descarga tu código es actions/___. (8 letras)", "checkout"),
  pr2=("La acción que guarda dependencias entre ejecuciones es actions/___. (5 letras)", "cache"),
  ec="usar acciones de autores desconocidos sin revisar", out=""),
K("Secretos de GitHub", d="valores cifrados que los workflows usan sin mostrarlos", u="usar claves y tokens en Actions sin escribirlos en el código",
  mas="Se crean en Settings → Secrets and variables → Actions y se usan como ${{ secrets.NOMBRE }}. GitHub los oculta en los registros. GITHUB_TOKEN viene incluido y sirve para operar sobre el propio repositorio.",
  k=["Los secretos se usan con ${{ secrets.NOMBRE }}.", "GitHub oculta los secretos en los registros.", "GITHUB_TOKEN viene incluido en cada workflow."],
  sit="Tu workflow debe desplegar en un servidor y necesita su contraseña, pero el repositorio es público. ¿Dónde la guardas?",
  cod="""- run: ./desplegar.sh
  env:
    CLAVE: ${{ secrets.CLAVE_SERVIDOR }}""", h="usa un secreto como variable de entorno",
  pr=("Los valores cifrados para Actions se llaman ___. (8 letras)", "secretos", "secrets"),
  pr2=("El token que viene incluido en cada workflow es GITHUB___. (6 caracteres)", "_token"),
  ec="imprimir un secreto en los registros con echo", out=""),
K("Matrices", d="estrategia que corre el mismo job con varias combinaciones", u="probar tu código en varias versiones y sistemas a la vez",
  mas="strategy.matrix con node: [18, 20, 22] y os: [ubuntu-latest, windows-latest] crea un job por combinación. Así sabes si tu librería funciona en todas. fail-fast: false deja terminar las demás aunque una falle.",
  k=["Una matriz crea un job por combinación.", "Con matrices se prueba en varias versiones a la vez.", "fail-fast: false deja terminar las demás combinaciones."],
  sit="Tu librería debe funcionar en Node 18, 20 y 22, en Linux y Windows. ¿Qué usas para probar todas las combinaciones?",
  cod="""strategy:
  matrix:
    node: [18, 20, 22]
    os: [ubuntu-latest, windows-latest]
runs-on: ${{ matrix.os }}""", h="seis combinaciones de versión y sistema",
  pr=("La clave de Actions para probar varias combinaciones es ___. (6 letras)", "matrix"),
  pr2=("La opción que no cancela las demás si una falla es fail-___: false. (4 letras)", "fast"),
  ec="crear seis workflows copiados en lugar de una matriz", out=""),
K("Artefactos", d="archivos que un workflow guarda para descargar o usar en otro job", u="conservar el resultado de un build o un informe de pruebas",
  mas="actions/upload-artifact guarda archivos (por ejemplo, dist/ o un informe) y actions/download-artifact los recupera en otro job. Se descargan desde la ejecución en la pestaña Actions y caducan a los 90 días por defecto.",
  k=["Los artefactos guardan archivos de un workflow.", "upload-artifact sube archivos de la ejecución.", "Los artefactos caducan después de un tiempo."],
  sit="Tu workflow compila la app y quieres descargar la carpeta dist que generó para revisarla. ¿Qué guardas?",
  cod="""- uses: actions/upload-artifact@v4
  with:
    name: web
    path: dist/""", h="guarda la carpeta dist como artefacto",
  pr=("Los archivos que guarda un workflow se llaman ___. (10 letras)", "artefactos", "artifacts"),
  pr2=("La acción que los recupera es actions/___-artifact. (8 letras)", "download"),
  ec="guardar artefactos enormes en cada ejecución", out=""),
]

E4 = [
K("GitHub Pages", d="hosting gratis de páginas estáticas desde un repositorio", u="publicar tu portafolio o la web de un proyecto",
  mas="En Settings → Pages eliges la rama (o GitHub Actions para Vite/React). La web queda en usuario.github.io/repositorio, o en usuario.github.io si el repositorio se llama así. Solo sirve archivos estáticos: no ejecuta PHP ni Python.",
  k=["GitHub Pages publica páginas estáticas gratis.", "Pages no ejecuta código de servidor.", "El repositorio usuario.github.io es tu sitio principal."],
  sit="Terminaste tu portafolio en HTML, CSS y JS y quieres publicarlo gratis con una URL. ¿Qué servicio de GitHub usas?",
  cod="""# Settings → Pages → Source: Deploy from a branch → main / (root)
# https://ana.github.io/portafolio/""", h="publica la rama main con Pages",
  pr=("El servicio de GitHub para publicar páginas estáticas es GitHub ___. (5 letras)", "pages"),
  pr2=("El dominio de Pages termina en .github.___. (2 letras)", "io"),
  ec="intentar publicar una app de PHP o Flask en Pages", out=""),
K("Releases", d="versiones publicadas con notas y archivos descargables", u="entregar versiones de tu proyecto a los usuarios",
  mas="Un release se basa en una etiqueta (v1.2.0), tiene notas de cambios (GitHub las genera solas) y archivos adjuntos como instaladores o .zip. gh release create v1.2.0 --generate-notes lo hace desde la terminal.",
  k=["Un release se basa en una etiqueta de Git.", "Los releases pueden llevar archivos adjuntos.", "GitHub genera las notas de cambios automáticamente."],
  sit="Terminaste la versión 1.0 de tu app de escritorio y quieres que la gente descargue el instalador. ¿Qué publicas en GitHub?",
  cod="""gh release create v1.0.0 instalador.exe --generate-notes""", h="publica una versión con su instalador",
  pr=("Una versión publicada en GitHub se llama ___. (7 letras)", "release"),
  pr2=("Un release se basa en una ___ de Git. (8 letras)", "etiqueta"),
  ec="publicar versiones sin notas de qué cambió", out="https://github.com/ana/app/releases/tag/v1.0.0"),
K("GitHub Packages", d="registro de paquetes y contenedores integrado en GitHub", u="publicar librerías npm o imágenes Docker junto a tu código",
  mas="GitHub Container Registry (ghcr.io) guarda imágenes de Docker y GitHub Packages también aloja paquetes npm, Maven o NuGet. Se autentica con GITHUB_TOKEN en Actions y los permisos siguen a los del repositorio.",
  k=["ghcr.io guarda imágenes de Docker.", "GitHub Packages aloja paquetes npm.", "En Actions se autentica con GITHUB_TOKEN."],
  sit="Quieres publicar la imagen Docker de tu API en el mismo lugar donde está tu código. ¿Qué registro usas?",
  cod="""docker tag mi-api ghcr.io/ana/mi-api:1.0
docker push ghcr.io/ana/mi-api:1.0""", h="sube una imagen al registro de GitHub",
  pr=("El registro de paquetes integrado se llama GitHub ___. (8 letras)", "packages"),
  pr2=("El dominio del registro de contenedores de GitHub es ___.io. (4 letras)", "ghcr"),
  ec="publicar imágenes privadas como públicas por error", out="1.0: digest: sha256:4a5b… size: 1573"),
K("Gists", d="fragmentos de código que se comparten con un enlace", u="compartir un ejemplo o una configuración sin crear un repositorio",
  mas="En gist.github.com pegas uno o varios archivos y obtienes un enlace. Pueden ser públicos o secretos (no listados, pero accesibles con el enlace). Cada gist es un pequeño repositorio de Git.",
  k=["Un gist comparte fragmentos de código con un enlace.", "Un gist secreto no aparece en listados.", "Cada gist es un pequeño repositorio de Git."],
  sit="Quieres compartir con tu profesor un archivo de configuración de 20 líneas sin crear un repositorio. ¿Qué usas?",
  cod="""gh gist create config.json --desc "Mi configuración\"""", h="crea un gist desde la terminal",
  pr=("Un fragmento de código compartido con enlace en GitHub es un ___. (4 letras)", "gist"),
  pr2=("Un gist no listado se llama ___. (7 letras)", "secreto"),
  ec="creer que un gist secreto es privado y poner claves", out="https://gist.github.com/ana/3f2a…"),
K("GitHub CLI", d="herramienta gh para usar GitHub desde la terminal", u="crear repositorios, issues y pull requests sin abrir el navegador",
  mas="gh auth login inicia sesión; gh repo create, gh issue list, gh pr create y gh pr checkout cubren el trabajo diario. También configura Git para hacer push por HTTPS sin tokens a mano.",
  k=["gh es la terminal oficial de GitHub.", "gh auth login inicia sesión en GitHub.", "gh pr checkout descarga un pull request."],
  sit="Quieres revisar en tu computador el pull request #15 de un compañero con una sola orden. ¿Qué herramienta usas?",
  cod="""gh auth login
gh pr checkout 15""", h="inicia sesión y descarga un pull request",
  pr=("La orden de la terminal de GitHub es ___. (2 letras)", "gh"),
  pr2=("Para iniciar sesión se usa gh auth ___. (5 letras)", "login"),
  ec="crear tokens a mano en lugar de usar gh auth login", out="Switched to branch 'arreglo-login'"),
K("Codespaces", d="entorno de VS Code en la nube para cualquier repositorio", u="programar desde cualquier computador sin instalar nada",
  mas="Desde Code → Codespaces se abre VS Code en el navegador con una máquina Linux en la nube y el repositorio listo. El archivo .devcontainer/devcontainer.json define qué herramientas instala. Tiene horas gratis al mes.",
  k=["Codespaces abre VS Code en la nube.", "devcontainer.json define el entorno de Codespaces.", "Codespaces tiene horas gratis al mes."],
  sit="Estás en un computador de la biblioteca sin permisos para instalar nada y debes trabajar en tu repositorio. ¿Qué usas?",
  cod="""{
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "postCreateCommand": "pip install -r requirements.txt"
}""", h="devcontainer.json con Python y dependencias",
  pr=("El entorno de VS Code en la nube de GitHub es ___. (10 letras)", "codespaces"),
  pr2=("El archivo que define el entorno es devcontainer.___. (4 letras)", "json"),
  ec="dejar codespaces encendidos y gastar las horas gratis", out=""),
K("Repositorios plantilla", d="repositorios marcados como plantilla para crear otros iguales", u="empezar proyectos nuevos con la estructura lista",
  mas="En Settings marcas Template repository y aparece el botón Use this template. El repositorio nuevo copia archivos y carpetas pero no el historial. Muy útil para proyectos de clase con la misma base.",
  k=["Una plantilla crea repositorios con la misma estructura.", "El botón Use this template crea la copia.", "El repositorio nuevo no copia el historial."],
  sit="Cada semestre creas el mismo esqueleto de proyecto Flask para tus estudiantes. ¿Qué tipo de repositorio te ahorra trabajo?",
  cod="""gh repo create proyecto-final --template ana/plantilla-flask --private""", h="crea un repositorio desde una plantilla",
  pr=("El botón para crear desde una plantilla es Use this ___. (8 letras)", "template"),
  pr2=("Un repositorio creado con plantilla no copia el ___. (9 letras)", "historial"),
  ec="hacer fork para empezar proyectos que no vas a devolver al original", out=""),
K("Wiki y proyectos de documentación", d="espacio de documentación de un repositorio", u="guardar guías largas fuera del README",
  mas="Cada repositorio puede tener una Wiki con páginas en Markdown y su propio historial. Para documentación grande se suele usar una carpeta docs/ con un generador (MkDocs, Docusaurus) publicado en Pages.",
  k=["La Wiki guarda páginas de documentación en Markdown.", "La carpeta docs/ puede publicarse con Pages.", "MkDocs genera sitios de documentación."],
  sit="Tu README ya es enorme con guías de instalación, arquitectura y API. ¿Dónde organizas esas guías en GitHub?",
  cod="""git clone https://github.com/ana/tienda.wiki.git""", h="clona la wiki de un repositorio",
  pr=("El espacio de documentación de un repositorio es la ___. (4 letras)", "wiki"),
  pr2=("La carpeta clásica de documentación es ___/. (4 letras)", "docs"),
  ec="tener la documentación desactualizada respecto al código", out="Cloning into 'tienda.wiki'..."),
]

E5 = [
K("Dependabot", d="robot de GitHub que avisa y actualiza dependencias vulnerables", u="mantener las librerías al día sin revisarlas a mano",
  mas="Dependabot alerts avisa si una dependencia tiene una vulnerabilidad conocida y Dependabot security updates abre el pull request que la corrige. Con .github/dependabot.yml también propone actualizaciones de versión cada semana.",
  k=["Dependabot avisa de dependencias vulnerables.", "Dependabot abre pull requests de actualización.", "dependabot.yml configura las actualizaciones."],
  sit="Una librería que usas tiene una vulnerabilidad grave y no te enteraste. ¿Qué función de GitHub te habría avisado?",
  cod="""# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: "/"
    schedule: { interval: weekly }""", h="actualizaciones semanales de npm",
  pr=("El robot de GitHub que actualiza dependencias es ___. (10 letras)", "dependabot"),
  pr2=("La frecuencia semanal se escribe interval: ___. (6 letras)", "weekly"),
  ec="ignorar las alertas de Dependabot durante meses", out=""),
K("Code scanning", d="análisis automático del código para encontrar vulnerabilidades", u="detectar inyecciones SQL, XSS y otros fallos antes de publicar",
  mas="Code scanning usa CodeQL para revisar el código en cada push o pull request y muestra las alertas en la pestaña Security. Es gratis en repositorios públicos. Se activa con el workflow de CodeQL.",
  k=["Code scanning busca vulnerabilidades en el código.", "Code scanning usa CodeQL.", "Las alertas aparecen en la pestaña Security."],
  sit="Quieres que GitHub revise automáticamente si tu código tiene una inyección SQL antes de unir cada pull request. ¿Qué activas?",
  cod="""- uses: github/codeql-action/init@v3
  with: { languages: python }
- uses: github/codeql-action/analyze@v3""", h="analiza el código de Python con CodeQL",
  pr=("El motor de análisis de code scanning es ___. (6 letras)", "codeql"),
  pr2=("Las alertas aparecen en la pestaña ___. (8 letras)", "security"),
  ec="desactivar las alertas en lugar de corregirlas", out=""),
K("Secret scanning", d="detección de claves y tokens subidos por error", u="evitar que tus credenciales queden expuestas",
  mas="GitHub revisa los commits buscando tokens conocidos (AWS, Stripe, GitHub…). Con push protection bloquea el push antes de que el secreto llegue. Si ya se subió, cambia la clave: borrarlo del archivo no basta porque queda en el historial.",
  k=["Secret scanning detecta claves subidas por error.", "Push protection bloquea el push con secretos.", "Una clave filtrada se debe cambiar."],
  sit="Subiste por error tu archivo .env con la clave de la base de datos a GitHub. ¿Qué es lo primero que debes hacer?",
  cod="""git push
# remote: error: GH013: Repository rule violations found
# remote: - Push cannot contain secrets""", h="push bloqueado porque contiene un secreto",
  pr=("La función que bloquea el push con secretos es push ___. (10 letras)", "protection"),
  pr2=("Una clave filtrada se debe ___. (7 letras)", "cambiar", "rotar"),
  ec="borrar el archivo en un commit nuevo y creer que ya no está", out=""),
K("Autenticación en dos pasos", d="segundo factor para entrar a tu cuenta además de la contraseña", u="que nadie entre a tu cuenta aunque sepa tu contraseña",
  mas="GitHub exige 2FA a quienes publican código. Puedes usar una app (Google Authenticator, Authy), llaves de seguridad o passkeys. Guarda los códigos de recuperación en un lugar seguro.",
  k=["2FA agrega un segundo factor a la contraseña.", "GitHub exige 2FA a quienes publican código.", "Los códigos de recuperación permiten entrar si pierdes el celular."],
  sit="Alguien consiguió tu contraseña de GitHub de una filtración. ¿Qué configuración le habría impedido entrar?",
  cod="""# Settings → Password and authentication → Enable two-factor authentication""", h="activa la autenticación en dos pasos",
  pr=("Las siglas de autenticación en dos pasos son ___. (3 caracteres)", "2fa"),
  pr2=("Si pierdes el celular entras con los códigos de ___. (11 letras)", "recuperacion", "recuperación"),
  ec="no guardar los códigos de recuperación", out=""),
K("GitHub Projects", d="tableros y tablas para planificar el trabajo con issues y PR", u="organizar un proyecto como un tablero Kanban",
  mas="Un Project reúne issues y pull requests de uno o varios repositorios en vistas de tablero (Por hacer, En progreso, Hecho), tabla o cronograma. Tiene campos propios como prioridad o fecha y automatizaciones.",
  k=["GitHub Projects organiza issues en tableros.", "Projects tiene vistas de tablero, tabla y cronograma.", "Un Project puede incluir varios repositorios."],
  sit="Tu equipo quiere ver en columnas qué tareas están por hacer, en progreso y terminadas. ¿Qué herramienta de GitHub usa?",
  cod="""gh project create --owner ana --title "Sprint 1\"""", h="crea un tablero de proyecto",
  pr=("La herramienta de tableros de GitHub es GitHub ___. (8 letras)", "projects"),
  pr2=("El tipo de tablero con columnas se llama ___. (6 letras)", "kanban"),
  ec="tener el tablero desactualizado y nadie lo mira", out=""),
K("Organizaciones y equipos", d="cuentas compartidas para grupos con equipos y permisos", u="que una empresa o un grupo de estudio administre sus repositorios",
  mas="Una organización es dueña de repositorios en lugar de una persona. Dentro creas equipos (teams) con permisos y CODEOWNERS indica quién debe revisar cada carpeta. Si alguien sale, el código sigue en la organización.",
  k=["Una organización es dueña de repositorios.", "Los equipos agrupan miembros con permisos.", "CODEOWNERS asigna revisores por carpeta."],
  sit="Tu grupo del SENA quiere que los repositorios del proyecto no dependan de la cuenta de una sola persona. ¿Qué crean en GitHub?",
  cod="""# .github/CODEOWNERS
/backend/  @equipo-backend
/frontend/ @ana""", h="asigna revisores por carpeta",
  pr=("Una cuenta compartida por un grupo es una ___. (12 letras)", "organizacion", "organización"),
  pr2=("El archivo que asigna revisores por carpeta es ___. (10 letras)", "codeowners"),
  ec="poner los repositorios del grupo en la cuenta personal de alguien", out=""),
K("Contribuir a open source", d="aportar a proyectos públicos de otras personas", u="aprender, ganar experiencia real y mejorar tu perfil",
  mas="Lee CONTRIBUTING.md y el código de conducta, busca issues con good first issue, haz fork, crea una rama, haz los cambios con pruebas y abre un pull request explicando qué y por qué. También cuentan la documentación y las traducciones.",
  k=["CONTRIBUTING.md explica cómo contribuir.", "Las contribuciones empiezan con un fork.", "La documentación también es una contribución."],
  sit="Quieres hacer tu primer aporte a una librería famosa que usas. ¿Qué archivo lees primero?",
  cod="""gh repo fork dueño/libreria --clone
git switch -c corrige-typo""", h="hace fork, clona y crea una rama",
  pr=("El archivo con las reglas para contribuir es ___.md. (12 letras)", "contributing"),
  pr2=("La copia de un repositorio en tu cuenta se llama ___. (4 letras)", "fork"),
  ec="abrir un pull request enorme sin hablar antes con los mantenedores", out="✓ Created fork ana/libreria"),
K("Perfil y portafolio en GitHub", d="tu página de GitHub como carta de presentación", u="mostrar tus proyectos a empresas y profesores",
  mas="Un repositorio con tu mismo nombre de usuario muestra su README en tu perfil. Fija (pin) tus seis mejores proyectos, con README, capturas y demo en Pages. La constancia de commits también cuenta.",
  k=["Un repositorio con tu nombre de usuario personaliza tu perfil.", "Puedes fijar hasta seis repositorios en tu perfil.", "Los proyectos con demo y README impresionan más."],
  sit="Vas a postularte a tu primer trabajo y quieres que el reclutador vea tus mejores proyectos en GitHub. ¿Qué preparas?",
  cod="""# Repositorio: ana/ana  →  README.md
## Hola, soy Ana 👋
Desarrolladora web · Python · React""", h="README especial del perfil",
  pr=("Para mostrar repositorios destacados en el perfil se ___. (5 letras)", "fijan", "pin"),
  pr2=("El README del perfil está en un repositorio con tu nombre de ___. (7 letras)", "usuario"),
  ec="tener solo repositorios vacíos o sin README", out=""),
]

ETAPAS_CONCEPTOS = [
    ("Empieza en GitHub", "Cuenta, repositorios, README, licencias y clonar", E1),
    ("Colabora en equipo", "Issues, pull requests, revisiones, conflictos y permisos", E2),
    ("GitHub Actions", "CI/CD: workflows, eventos, jobs, secretos y matrices", E3),
    ("Publica y comparte", "Pages, releases, paquetes, gists, CLI y Codespaces", E4),
    ("Seguridad y comunidad", "Dependabot, escaneo, 2FA, Projects, organizaciones y open source", E5),
    ("Trabaja como en una empresa", "Rulesets, CODEOWNERS, borradores, auto-merge, milestones y búsquedas", E6),
    ("Actions a fondo", "Caché, contextos, condiciones, entornos, reutilización, OIDC y depuración", E7),
    ("API, automatización y comunidad", "API REST y GraphQL, apps, webhooks, Copilot y open source", E8),
]
