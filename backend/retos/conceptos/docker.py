"""Docker: contenedores, imágenes, Dockerfile y Compose. 3 etapas."""
from ..generador import K
from .docker_e45 import E4, E5
from .docker_e678 import E6, E7, E8

E1 = [
K("Qué es Docker", d="herramienta que empaqueta aplicaciones en contenedores", u="que una app funcione igual en cualquier computador o servidor",
  mas="Docker mete la app junto con todo lo que necesita (sistema base, librerías, configuración) en un contenedor aislado. Así se acaba el «en mi computador sí funciona». Docker Desktop lo instala en Windows y macOS; en Linux se instala Docker Engine.",
  k=["Docker empaqueta una app con todo lo que necesita.", "Un contenedor funciona igual en cualquier máquina.", "Docker Desktop instala Docker en Windows y macOS."],
  sit="Tu app funciona en tu computador pero falla en el de tu compañero por versiones distintas. ¿Qué herramienta lo evita?",
  cod="""docker --version""", h="comprueba que Docker está instalado",
  pr=("La herramienta que empaqueta apps en contenedores es ___. (6 letras)", "docker"),
  pr2=("En Windows y macOS, Docker se instala con Docker ___. (7 letras)", "desktop"),
  ec="pensar que Docker es una máquina virtual completa", out="Docker version 27.3.1"),
K("Imagen", d="plantilla de solo lectura con todo lo necesario para crear contenedores", u="distribuir una app lista para ejecutarse",
  mas="Una imagen contiene el sistema base, las dependencias y tu código, organizados en capas. Se identifica con nombre:etiqueta, como node:20 o mysql:8. Las imágenes se descargan de registros como Docker Hub.",
  k=["Una imagen es una plantilla para crear contenedores.", "Las imágenes se nombran como nombre:etiqueta.", "Docker Hub es un registro público de imágenes."],
  sit="Quieres la plantilla oficial de MySQL 8 lista para crear contenedores a partir de ella. ¿Qué descargas?",
  cod="""docker pull mysql:8   # descarga la imagen
docker images         # lista las imágenes locales""", h="descarga una imagen y lista las que tienes",
  pr=("La orden que descarga una imagen es docker ___. (4 letras)", "pull"),
  pr2=("El registro público de imágenes de Docker es Docker ___. (3 letras)", "hub"),
  ec="usar la etiqueta latest en producción y recibir cambios inesperados", out="REPOSITORY   TAG   IMAGE ID       SIZE\nmysql        8     3c1fd0a2b4e7   586MB"),
K("Contenedor", d="instancia en ejecución de una imagen", u="ejecutar una app aislada del resto del sistema",
  mas="Un contenedor se crea a partir de una imagen con docker run. Tiene su propio sistema de archivos, procesos y red. Puedes crear muchos contenedores de la misma imagen, detenerlos, reiniciarlos o borrarlos sin afectar la imagen.",
  k=["Un contenedor es una imagen en ejecución.", "De una misma imagen se pueden crear muchos contenedores.", "Borrar un contenedor no borra su imagen."],
  sit="Ya tienes la imagen de nginx y quieres ponerla a funcionar como un servidor web aislado. ¿Qué creas?",
  cod="""docker run -d --name web -p 8080:80 nginx""", h="ejecuta nginx en segundo plano y lo publica en el puerto 8080",
  pr=("La orden que crea y ejecuta un contenedor es docker ___. (3 letras)", "run"),
  pr2=("La opción -___ de docker run lo deja en segundo plano. (1 letra)", "d"),
  ec="confundir la imagen, que es la plantilla, con el contenedor", out="a41c9e7b2d58f0e3c6..."),
K("Puertos", d="conexión entre un puerto de tu computador y uno del contenedor", u="poder abrir en el navegador la app que corre dentro del contenedor",
  mas="La opción -p puertoHost:puertoContenedor publica un puerto. Con -p 8080:80, al abrir localhost:8080 llegas al puerto 80 del contenedor. Sin -p, la app funciona pero no puedes entrar desde fuera.",
  k=["La opción -p publica un puerto del contenedor.", "En -p 8080:80 el primer número es el de tu computador.", "Sin -p no se puede entrar a la app desde fuera."],
  sit="El contenedor de tu app escucha en el puerto 3000 y quieres abrirla en el navegador como localhost:3000. ¿Qué opción agregas?",
  cod="""docker run -d -p 3000:3000 mi-app""", h="publica el puerto 3000 del contenedor en tu computador",
  pr=("La opción de docker run que publica puertos es -___. (1 letra)", "p"),
  pr2=("En -p 8080:80, el número 80 es el puerto del ___. (10 letras)", "contenedor"),
  ec="invertir el orden de los puertos en la opción -p", out=""),
K("docker ps y logs", d="órdenes para ver contenedores y su salida", u="saber qué está corriendo y por qué algo falla",
  mas="docker ps lista los contenedores en ejecución; con -a también los detenidos. docker logs nombre muestra lo que imprimió la app y -f lo sigue en vivo. Son lo primero que se revisa cuando algo no funciona.",
  k=["docker ps lista los contenedores en ejecución.", "docker ps -a incluye los contenedores detenidos.", "docker logs muestra la salida de un contenedor."],
  sit="Tu contenedor se detuvo solo y quieres ver qué mensajes de error imprimió la app. ¿Qué orden usas?",
  cod="""docker ps -a
docker logs -f web""", h="lista todos los contenedores y sigue los mensajes de uno",
  pr=("La orden que lista los contenedores es docker ___. (2 letras)", "ps"),
  pr2=("Para seguir los logs en vivo se usa docker logs -___. (1 letra)", "f"),
  ec="adivinar el error sin revisar los logs", out="CONTAINER ID   IMAGE   STATUS          NAMES\na41c9e7b2d58   nginx   Up 2 minutes    web"),
K("Ciclo de vida", d="órdenes para detener, iniciar y borrar contenedores", u="administrar tus contenedores sin dejar basura",
  mas="docker stop detiene, docker start vuelve a iniciar y docker rm borra un contenedor detenido. docker rmi borra imágenes y docker system prune limpia lo que no se usa. docker exec -it nombre sh abre una terminal dentro del contenedor.",
  k=["docker stop detiene un contenedor en ejecución.", "docker rm borra un contenedor detenido.", "docker exec -it abre una terminal dentro del contenedor."],
  sit="Quieres entrar a la terminal de un contenedor que está corriendo para revisar sus archivos. ¿Qué orden usas?",
  cod="""docker exec -it web sh   # terminal dentro del contenedor
docker stop web
docker rm web""", h="entra al contenedor, lo detiene y lo borra",
  pr=("La orden que abre una terminal en un contenedor es docker ___ -it. (4 letras)", "exec"),
  pr2=("La orden que borra una imagen es docker ___. (3 letras)", "rmi"),
  ec="acumular contenedores detenidos que ocupan espacio", out="web\nweb"),
]

E2 = [
K("Dockerfile", d="archivo con las instrucciones para construir una imagen", u="crear la imagen de tu propia aplicación",
  mas="FROM elige la imagen base, WORKDIR la carpeta de trabajo, COPY copia archivos, RUN ejecuta órdenes al construir, EXPOSE documenta el puerto y CMD indica qué se ejecuta al iniciar. Cada instrucción crea una capa.",
  k=["Un Dockerfile describe cómo construir una imagen.", "FROM indica la imagen base.", "CMD indica qué se ejecuta al iniciar el contenedor."],
  sit="Quieres convertir tu app de Node en una imagen propia que cualquiera pueda ejecutar con Docker. ¿Qué archivo escribes?",
  cod="""FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]""", h="construye la imagen de una app de Node",
  pr=("La instrucción que elige la imagen base es ___. (4 letras)", "from"),
  pr2=("La instrucción que ejecuta órdenes al construir la imagen es ___. (3 letras)", "run"),
  ec="copiar todo el código antes de instalar dependencias y perder la caché", out=""),
K("docker build", d="orden que construye una imagen a partir de un Dockerfile", u="generar la imagen de tu app para ejecutarla o publicarla",
  mas="docker build -t nombre:etiqueta . construye usando el Dockerfile de la carpeta actual (el punto). Docker reutiliza capas que no cambiaron, por eso conviene copiar primero package.json e instalar, y después el resto del código.",
  k=["docker build construye una imagen desde un Dockerfile.", "La opción -t le pone nombre a la imagen.", "Docker reutiliza las capas que no cambiaron."],
  sit="Ya escribiste el Dockerfile y quieres crear la imagen mi-app:1.0 desde la carpeta actual. ¿Qué orden usas?",
  cod="""docker build -t mi-app:1.0 .
docker run -d -p 3000:3000 mi-app:1.0""", h="construye la imagen y crea un contenedor con ella",
  pr=("La opción de docker build que pone nombre a la imagen es -___. (1 letra)", "t"),
  pr2=("Al final de docker build, el punto indica la carpeta ___. (6 letras)", "actual"),
  ec="olvidar el punto final de docker build", out="Successfully tagged mi-app:1.0"),
K(".dockerignore", d="archivo que excluye archivos al construir la imagen", u="imágenes más pequeñas, rápidas y sin secretos",
  mas="Funciona como .gitignore pero para docker build: lo listado no se envía al construir. Normalmente incluye node_modules, .git, .env y archivos de logs. Así la imagen pesa menos y no lleva claves dentro.",
  k=[".dockerignore excluye archivos al construir la imagen.", "node_modules suele ir en .dockerignore.", ".dockerignore evita meter secretos en la imagen."],
  sit="Tu imagen pesa demasiado porque se copia node_modules y además se cuela el archivo .env. ¿Qué archivo creas?",
  cod="""# .dockerignore
node_modules
.git
.env""", h="excluye dependencias, el historial y los secretos de la imagen",
  pr=("El archivo que excluye cosas al construir una imagen es ___. (13 caracteres)", ".dockerignore"),
  pr2=(".dockerignore funciona parecido a .___. (9 caracteres)", "gitignore"),
  ec="meter el archivo .env con claves dentro de la imagen", out=""),
K("Volúmenes", d="almacenamiento que sobrevive aunque borres el contenedor", u="no perder los datos de una base de datos en Docker",
  mas="Lo que se escribe dentro de un contenedor se pierde al borrarlo. Un volumen (-v datos:/var/lib/mysql) guarda esa carpeta fuera del contenedor. También puedes montar una carpeta de tu computador para editar código en vivo.",
  k=["Un volumen guarda datos fuera del contenedor.", "Sin volumen, los datos se pierden al borrar el contenedor.", "La opción -v monta un volumen en una carpeta."],
  sit="Corres MySQL en Docker y no quieres perder las tablas cada vez que borras y recreas el contenedor. ¿Qué usas?",
  cod="""docker volume create datos
docker run -d -v datos:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=clave mysql:8""", h="guarda los datos de MySQL en un volumen",
  pr=("El almacenamiento que sobrevive al contenedor se llama ___. (7 letras)", "volumen"),
  pr2=("La opción de docker run que monta un volumen es -___. (1 letra)", "v"),
  ec="guardar datos importantes sin volumen y perderlos", out="datos"),
K("Variables en contenedores", d="configuración que se pasa al contenedor al crearlo", u="usar la misma imagen con distintas claves y entornos",
  mas="-e NOMBRE=valor pasa una variable de entorno; --env-file .env pasa todas las de un archivo. Las imágenes oficiales (MySQL, PostgreSQL) se configuran así: contraseña, base inicial, usuario. Así no escribes secretos en el Dockerfile.",
  k=["La opción -e pasa una variable de entorno al contenedor.", "--env-file carga las variables desde un archivo.", "Las imágenes oficiales se configuran con variables."],
  sit="Quieres crear un contenedor de PostgreSQL con una contraseña propia sin escribirla en el Dockerfile. ¿Qué opción usas?",
  cod="""docker run -d -e POSTGRES_PASSWORD=secreta -p 5432:5432 postgres:16""", h="crea PostgreSQL con su contraseña por variable",
  pr=("La opción de docker run que pasa una variable de entorno es -___. (1 letra)", "e"),
  pr2=("Para cargar variables desde un archivo se usa --env-___. (4 letras)", "file"),
  ec="escribir contraseñas dentro del Dockerfile", out=""),
K("Redes", d="conexiones entre contenedores para que se hablen", u="que tu app se conecte a su base de datos dentro de Docker",
  mas="Los contenedores de una misma red se encuentran por su nombre: la app puede conectarse al host «db» en lugar de una IP. docker network create crea una red y --network la usa. Docker Compose crea una red automáticamente.",
  k=["Los contenedores de una red se encuentran por su nombre.", "docker network create crea una red.", "Docker Compose crea una red automáticamente."],
  sit="Tu contenedor de la app necesita conectarse al contenedor de la base de datos usando su nombre «db». ¿Qué los une?",
  cod="""docker network create mi-red
docker run -d --name db --network mi-red mysql:8
docker run -d --name app --network mi-red mi-app""", h="pone la app y la base en la misma red",
  pr=("La orden que crea una red es docker network ___. (6 letras)", "create"),
  pr2=("Dentro de una red, un contenedor se encuentra por su ___. (6 letras)", "nombre"),
  ec="usar localhost para conectar dos contenedores distintos", out=""),
]

E3 = [
K("Docker Compose", d="herramienta para definir y levantar varios contenedores juntos", u="arrancar app, base de datos y más con una sola orden",
  mas="En compose.yaml (o docker-compose.yml) describes los servicios: imagen o build, puertos, variables, volúmenes y dependencias. docker compose up -d levanta todo y docker compose down lo detiene.",
  k=["Docker Compose levanta varios contenedores juntos.", "Los servicios se describen en compose.yaml.", "docker compose down detiene todos los servicios."],
  sit="Tu proyecto necesita la app, MySQL y Redis, y quieres levantarlos todos juntos con una sola orden. ¿Qué usas?",
  cod="""services:
  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: clave
  app:
    build: .
    ports: ["3000:3000"]
    depends_on: [db]""", h="define la app y su base de datos como servicios",
  pr=("La herramienta que levanta varios contenedores juntos es Docker ___. (7 letras)", "compose"),
  pr2=("Para levantar los servicios en segundo plano usas docker compose up -___. (1 letra)", "d"),
  ec="levantar cada contenedor a mano en vez de usar Compose", out=""),
K("depends_on y healthcheck", d="opciones de Compose para el orden de arranque", u="que la app no arranque antes de que la base de datos esté lista",
  mas="depends_on indica qué servicio arranca primero. Con un healthcheck, Compose puede esperar a que el servicio esté sano (condition: service_healthy). Aun así, conviene que la app reintente la conexión.",
  k=["depends_on define el orden de arranque de los servicios.", "Un healthcheck comprueba si un servicio está listo.", "La app debe reintentar la conexión a la base."],
  sit="Tu app falla al iniciar porque intenta conectarse a la base de datos antes de que esté lista. ¿Qué opción de Compose usas?",
  cod="""  db:
    image: mysql:8
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
  app:
    depends_on:
      db:
        condition: service_healthy""", h="hace que la app espere a que MySQL esté sana",
  pr=("La opción de Compose que define el orden de arranque es depends___. (3 caracteres)", "_on"),
  pr2=("La comprobación de que un servicio está listo se llama ___. (11 letras)", "healthcheck"),
  ec="suponer que el servicio arrancado ya está listo para conexiones", out=""),
K("Docker y XAMPP", d="dos formas de tener servidores de desarrollo en tu computador", u="elegir cómo correr MySQL, Apache o PHP para tus proyectos",
  mas="XAMPP instala Apache, MySQL (MariaDB) y PHP directamente en tu sistema, con un panel para encenderlos. Docker los corre aislados y con versiones exactas por proyecto. Si ambos usan el puerto 3306, hay que detener uno o cambiar el puerto.",
  k=["XAMPP instala Apache, MariaDB y PHP en tu sistema.", "Docker permite versiones distintas de MySQL por proyecto.", "XAMPP y Docker chocan si usan el mismo puerto."],
  sit="Ya tienes MySQL de XAMPP en el puerto 3306 y quieres además un MySQL 8 en Docker sin que choquen. ¿Qué cambias?",
  cod="""# XAMPP usa 3306; Docker usará 3307 en tu computador
docker run -d -p 3307:3306 -e MYSQL_ROOT_PASSWORD=clave mysql:8
mysql -h 127.0.0.1 -P 3307 -u root -p""", h="corre MySQL en Docker en otro puerto para no chocar con XAMPP",
  pr=("El puerto por defecto de MySQL es ___. (4 dígitos)", "3306"),
  pr2=("XAMPP incluye Apache, MariaDB y el lenguaje ___. (3 letras)", "php"),
  ec="encender XAMPP y Docker en el mismo puerto", out="Welcome to the MySQL monitor."),
K("Registros e imágenes propias", d="publicar tus imágenes para usarlas en otro lugar", u="desplegar tu app en servidores sin volver a construirla",
  mas="Etiquetas la imagen con tu usuario (docker tag mi-app ana/mi-app:1.0), inicias sesión con docker login y la subes con docker push. Además de Docker Hub existen GitHub Container Registry (ghcr.io) y los registros de la nube.",
  k=["docker push sube una imagen a un registro.", "docker login inicia sesión en un registro.", "GitHub también ofrece un registro de imágenes."],
  sit="Construiste tu imagen y quieres subirla a Docker Hub para descargarla en el servidor. ¿Qué orden usas al final?",
  cod="""docker tag mi-app:1.0 ana/mi-app:1.0
docker login
docker push ana/mi-app:1.0""", h="etiqueta, inicia sesión y sube la imagen",
  pr=("La orden que sube una imagen a un registro es docker ___. (4 letras)", "push"),
  pr2=("El registro de imágenes de GitHub usa el dominio ___.io. (4 letras)", "ghcr"),
  ec="subir imágenes con secretos dentro a un registro público", out="1.0: digest: sha256:9f2c... size: 1784"),
K("Imágenes livianas", d="técnicas para que las imágenes pesen poco y sean seguras", u="despliegues más rápidos y con menos riesgos",
  mas="Usa bases pequeñas (alpine o slim), instala solo lo necesario y usa construcción en varias etapas (multi-stage): una etapa compila y la final solo copia el resultado. También conviene no ejecutar como root (USER).",
  k=["Las imágenes alpine son mucho más pequeñas.", "Un build multi-stage deja fuera las herramientas de compilación.", "La instrucción USER evita ejecutar como root."],
  sit="Tu imagen de React pesa 1 GB porque incluye todas las herramientas de compilación. ¿Qué técnica la reduce?",
  cod="""FROM node:20-alpine AS build
WORKDIR /app
COPY . .
RUN npm ci && npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html""", h="compila en una etapa y sirve solo el resultado con nginx",
  pr=("La técnica de construir en varias etapas se llama multi-___. (5 letras)", "stage"),
  pr2=("La variante de imagen muy pequeña más usada es ___. (6 letras)", "alpine"),
  ec="dejar compiladores y herramientas de desarrollo en la imagen final", out=""),
K("Docker en producción", d="buenas prácticas para correr contenedores en servidores reales", u="que tu app esté disponible, segura y fácil de actualizar",
  mas="Fija versiones de las imágenes, usa --restart unless-stopped para que se recupere sola, guarda datos en volúmenes y los secretos en variables o gestores de secretos. Para muchos servidores se usan orquestadores como Kubernetes.",
  k=["--restart unless-stopped reinicia el contenedor si falla.", "En producción se fijan las versiones de las imágenes.", "Kubernetes orquesta contenedores en muchos servidores."],
  sit="Quieres que tu contenedor vuelva a arrancar solo si el servidor se reinicia o la app se cae. ¿Qué opción usas?",
  cod="""docker run -d --restart unless-stopped -p 80:3000 ana/mi-app:1.0""", h="ejecuta la app con reinicio automático",
  pr=("La opción que reinicia un contenedor que falla es --___. (7 letras)", "restart"),
  pr2=("El orquestador de contenedores más usado es ___. (10 letras)", "kubernetes"),
  ec="usar la etiqueta latest en producción", out=""),
]

ETAPAS_CONCEPTOS = [
    ("Contenedores e imágenes", "Ejecuta y administra contenedores", E1),
    ("Crea tus imágenes", "Dockerfile, build, volúmenes, variables y redes", E2),
    ("Compose y producción", "Varios servicios, XAMPP, registros y buenas prácticas", E3),
    ("Docker a fondo", "exec, inspect, caché, multi-stage, seguridad y limpieza", E4),
    ("Orquestación y nube", "Compose avanzado, Kubernetes, CI y despliegue", E5),
    ("Docker para tus proyectos", "Flask, FastAPI, Django, React, PHP y bases de datos en contenedores", E6),
    ("Imágenes y seguridad", "ARG, etiquetas, registros, escaneo, BuildKit, límites y contenedores seguros", E7),
    ("Kubernetes y producción", "ConfigMaps, Ingress, probes, escalado, Helm, Swarm y monitoreo", E8),
]

from .docker_ref import ETAPAS_REF as _REF
ETAPAS_CONCEPTOS = ETAPAS_CONCEPTOS + _REF   # etapas de referencia: más temas del curso
