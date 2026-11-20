"""Docker, etapas 4 y 5: Docker a fondo y orquestación en la nube."""
from ..generador import K

E4 = [
K("docker exec", d="orden que ejecuta un comando dentro de un contenedor que ya corre", u="entrar a un contenedor para revisar archivos o la base de datos",
  mas="docker exec -it mi-web sh abre una terminal dentro del contenedor (bash si la imagen lo trae). docker exec mi-db mysql -u root -p entra al MySQL del contenedor. -it hace la sesión interactiva.",
  k=["docker exec ejecuta un comando en un contenedor activo.", "docker exec -it abre una sesión interactiva.", "El contenedor debe estar corriendo para usar exec."],
  sit="Tu contenedor de MySQL está corriendo y quieres entrar a su consola para revisar una tabla. ¿Qué orden usas?",
  cod="""docker exec -it mi-db mysql -u root -p""", h="abre la consola de MySQL dentro del contenedor",
  pr=("La orden que ejecuta un comando dentro de un contenedor activo es docker ___. (4 letras)", "exec"),
  pr2=("Las opciones para una sesión interactiva son -___. (2 letras)", "it"),
  ec="hacer cambios a mano dentro del contenedor y perderlos al recrearlo", out="Enter password:\nmysql>"),
K("docker inspect", d="orden que muestra toda la configuración de un contenedor o imagen en JSON", u="ver la IP, los puertos, los volúmenes o las variables de un contenedor",
  mas="docker inspect mi-web devuelve un JSON enorme. Con --format se saca un dato: docker inspect -f '{{.NetworkSettings.IPAddress}}' mi-web. También sirve con imágenes, volúmenes y redes.",
  k=["docker inspect muestra la configuración en JSON.", "docker inspect -f extrae un solo dato.", "inspect funciona con contenedores, imágenes y redes."],
  sit="Necesitas saber qué variables de entorno y volúmenes tiene montados un contenedor que alguien creó. ¿Qué orden usas?",
  cod="""docker inspect -f '{{.State.Status}}' mi-web""", h="muestra solo el estado del contenedor",
  pr=("La orden que muestra la configuración completa en JSON es docker ___. (7 letras)", "inspect"),
  pr2=("La opción de inspect que saca un solo dato es -___. (1 letra)", "f"),
  ec="buscar a ojo en todo el JSON en lugar de usar --format", out="running"),
K("Capas y caché de build", d="cada instrucción del Dockerfile crea una capa que Docker reutiliza", u="que las imágenes se construyan en segundos y no en minutos",
  mas="Si una línea y las anteriores no cambiaron, Docker usa la capa guardada (CACHED). Por eso se copia primero package.json o requirements.txt, se instalan las dependencias y al final se copia el código: cambiar el código no reinstala todo.",
  k=["Cada instrucción del Dockerfile crea una capa.", "Docker reutiliza las capas que no cambiaron.", "Copiar primero las dependencias aprovecha la caché."],
  sit="Cada vez que cambias una línea de tu código, docker build vuelve a instalar todas las dependencias y tarda 5 minutos. ¿Qué aprovechas reordenando el Dockerfile?",
  cod="""FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .""", h="instala dependencias antes de copiar el código",
  pr=("Cada instrucción del Dockerfile crea una ___. (4 letras)", "capa"),
  pr2=("Cuando Docker reutiliza una capa, el build muestra ___. (6 letras)", "cached"),
  ec="copiar todo el código antes de instalar las dependencias", out=" => CACHED [3/5] COPY package*.json ./"),
K("Multi-stage build", d="Dockerfile con varias etapas FROM donde la final solo copia lo necesario", u="imágenes de producción pequeñas sin herramientas de compilación",
  mas="La primera etapa (AS build) instala todo y compila; la última empieza desde una imagen liviana y usa COPY --from=build para traer solo el resultado. Una app de React pasa de 1 GB a unos 25 MB con nginx.",
  k=["Un multi-stage build tiene varias instrucciones FROM.", "COPY --from copia archivos de otra etapa.", "La imagen final solo lleva lo necesario."],
  sit="Tu imagen de React pesa 1 GB porque lleva Node y todo node_modules, pero solo necesitas servir la carpeta dist. ¿Qué técnica usas?",
  cod="""FROM node:20 AS build
WORKDIR /app
COPY . .
RUN npm ci && npm run build
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html""", h="compila con Node y sirve el resultado con nginx",
  pr=("Para copiar desde otra etapa se usa COPY --___. (4 letras)", "from"),
  pr2=("Para nombrar una etapa se escribe FROM imagen ___ nombre. (2 letras)", "as"),
  ec="dejar compiladores y código fuente en la imagen final", out=""),
K("CMD y ENTRYPOINT", d="instrucciones que definen qué ejecuta el contenedor al arrancar", u="decidir el programa principal y sus argumentos por defecto",
  mas="CMD [\"npm\", \"start\"] es la orden por defecto y se reemplaza al escribir otra en docker run. ENTRYPOINT fija el programa y CMD pasa a ser sus argumentos. Se usa la forma de lista JSON para que reciba bien las señales.",
  k=["CMD se reemplaza con lo que escribes en docker run.", "ENTRYPOINT fija el programa principal.", "La forma de lista JSON recibe bien las señales."],
  sit="Quieres que tu imagen siempre ejecute python, pero que el archivo a correr se pueda cambiar al hacer docker run. ¿Qué combinación usas?",
  cod="""ENTRYPOINT ["python"]
CMD ["app.py"]""", h="ejecuta python app.py, o python con otro archivo",
  pr=("La instrucción que fija el programa principal es ___. (10 letras)", "entrypoint"),
  pr2=("La instrucción con la orden por defecto que se puede reemplazar es ___. (3 letras)", "cmd"),
  ec="usar la forma de texto y que Ctrl+C no detenga el contenedor", out=""),
K("Usuario no root", d="ejecutar el proceso del contenedor con un usuario sin privilegios", u="que una falla en tu app no le dé control total del contenedor",
  mas="Por defecto los contenedores corren como root. Con RUN adduser y USER app (o el usuario node de la imagen oficial de Node) el proceso tiene menos permisos. Es una de las primeras reglas de seguridad en producción.",
  k=["Los contenedores corren como root por defecto.", "La instrucción USER cambia el usuario del proceso.", "La imagen oficial de Node trae el usuario node."],
  sit="Una auditoría de seguridad dice que tu contenedor de Node no debe ejecutarse como root. ¿Qué instrucción agregas al Dockerfile?",
  cod="""FROM node:20-alpine
WORKDIR /app
COPY --chown=node:node . .
USER node
CMD ["node", "server.js"]""", h="ejecuta la app con el usuario node",
  pr=("La instrucción del Dockerfile que cambia el usuario es ___. (4 letras)", "user"),
  pr2=("Por defecto, el proceso de un contenedor corre como ___. (4 letras)", "root"),
  ec="cambiar a USER antes de copiar archivos y quedarse sin permisos", out=""),
K("Bind mounts", d="montar una carpeta de tu computador dentro del contenedor", u="ver tus cambios de código al instante mientras desarrollas",
  mas="docker run -v $(pwd):/app monta la carpeta actual en /app: lo que guardas en VS Code se ve en el contenedor. Los volúmenes (-v datos:/var/lib/mysql) los maneja Docker y son mejores para bases de datos.",
  k=["Un bind mount monta una carpeta del computador.", "Con bind mounts los cambios se ven al instante.", "Para bases de datos conviene un volumen de Docker."],
  sit="Desarrollas en un contenedor y no quieres reconstruir la imagen cada vez que cambias una línea. ¿Qué tipo de montaje usas?",
  cod="""docker run -p 3000:3000 -v "$(pwd)":/app -w /app node:20 npm run dev""", h="monta la carpeta actual y arranca el servidor de desarrollo",
  pr=("Montar una carpeta del computador en el contenedor se llama bind ___. (5 letras)", "mount"),
  pr2=("La opción de docker run que monta carpetas o volúmenes es -___. (1 letra)", "v"),
  ec="usar bind mounts en producción en lugar de copiar el código en la imagen", out="  VITE ready in 312 ms"),
K("docker system prune", d="orden que borra contenedores detenidos, redes e imágenes sin usar", u="recuperar espacio en disco",
  mas="docker system df muestra cuánto ocupa Docker. docker system prune borra lo que no se usa y con -a también las imágenes sin contenedor. --volumes borra volúmenes: cuidado, ahí pueden estar tus bases de datos.",
  k=["docker system prune borra lo que no se usa.", "docker system df muestra el espacio usado.", "prune --volumes puede borrar datos de bases."],
  sit="Tu disco está lleno y Docker ocupa 40 GB en imágenes y contenedores viejos. ¿Qué orden limpia lo que no se usa?",
  cod="""docker system df
docker system prune""", h="muestra el espacio usado y limpia lo que sobra",
  pr=("La orden que limpia lo que Docker no usa es docker system ___. (5 letras)", "prune"),
  pr2=("La orden que muestra el espacio que ocupa Docker es docker system ___. (2 letras)", "df"),
  ec="usar prune --volumes y borrar la base de datos", out="Total reclaimed space: 12.4GB"),
]

E5 = [
K("Perfiles de Compose", d="grupos de servicios que solo se encienden si los pides", u="tener herramientas extra (como phpMyAdmin) solo cuando las necesitas",
  mas="Un servicio con profiles: [\"herramientas\"] no arranca con docker compose up. Se enciende con docker compose --profile herramientas up. Así el entorno diario arranca rápido y lo extra queda a mano.",
  k=["Los servicios con perfil no arrancan por defecto.", "--profile enciende los servicios de un perfil.", "Los perfiles se declaran con profiles en el servicio."],
  sit="Quieres que phpMyAdmin esté en tu compose.yaml pero que no arranque cada vez, solo cuando lo necesitas. ¿Qué usas?",
  cod="""services:
  phpmyadmin:
    image: phpmyadmin
    profiles: ["herramientas"]""", h="phpMyAdmin solo arranca con su perfil",
  pr=("La clave de Compose para agrupar servicios opcionales es ___. (8 letras)", "profiles"),
  pr2=("Se encienden con docker compose --___ nombre up. (7 letras)", "profile"),
  ec="crear varios archivos compose casi iguales en lugar de usar perfiles", out=""),
K("Escalar servicios", d="ejecutar varias copias del mismo servicio", u="atender más usuarios repartiendo el trabajo",
  mas="docker compose up --scale api=3 crea tres contenedores de la API. Para repartir el tráfico se pone delante un proxy (nginx, Traefik). Los servicios escalables no deben guardar datos en el propio contenedor.",
  k=["--scale crea varias copias de un servicio.", "Un proxy reparte el tráfico entre copias.", "Un servicio escalable no guarda datos dentro del contenedor."],
  sit="Tu API recibe tantas peticiones que un solo contenedor no da abasto. ¿Qué opción de Compose crea más copias?",
  cod="""docker compose up -d --scale api=3
docker compose ps""", h="levanta tres copias de la API",
  pr=("La opción que crea varias copias de un servicio es --___. (5 letras)", "scale"),
  pr2=("Lo que reparte el tráfico entre copias es un ___. (5 letras)", "proxy"),
  ec="escalar un servicio que usa ports fijos y chocar de puertos", out="api-1   running\napi-2   running\napi-3   running"),
K("Kubernetes", d="orquestador que gestiona contenedores en muchos servidores", u="mantener apps vivas, escalarlas y actualizarlas sin cortes",
  mas="Kubernetes (K8s) reinicia contenedores que fallan, reparte la carga y actualiza versiones poco a poco. Lo ofrecen las nubes (GKE, EKS, AKS) y se practica en local con minikube, kind o Docker Desktop.",
  k=["Kubernetes orquesta contenedores en varios servidores.", "Kubernetes reinicia los contenedores que fallan.", "minikube crea un Kubernetes local para practicar."],
  sit="Tu empresa tiene 50 servicios en contenedores repartidos en muchos servidores y necesita que se recuperen solos. ¿Qué plataforma usa?",
  cod="""minikube start
kubectl get nodes""", h="arranca un Kubernetes local y lista sus nodos",
  pr=("La abreviatura de Kubernetes es ___. (3 caracteres)", "k8s"),
  pr2=("La herramienta para practicar Kubernetes en local es ___. (8 letras)", "minikube"),
  ec="usar Kubernetes para un proyecto pequeño que basta con Compose", out="NAME       STATUS   ROLES           AGE   VERSION\nminikube   Ready    control-plane   1m    v1.31.0"),
K("Pods", d="la unidad más pequeña de Kubernetes: uno o más contenedores juntos", u="ejecutar tu contenedor dentro de un clúster",
  mas="Un pod comparte red y almacenamiento entre sus contenedores. Los pods son efímeros: si mueren, Kubernetes crea otros nuevos con otra IP. Por eso casi nunca se crean a mano, sino con un Deployment.",
  k=["Un pod es la unidad más pequeña de Kubernetes.", "Los contenedores de un pod comparten la red.", "Los pods son efímeros y se reemplazan."],
  sit="En Kubernetes, ¿cómo se llama la unidad donde realmente corre tu contenedor?",
  cod="""kubectl get pods
kubectl logs mi-api-7d9f8-abcde""", h="lista los pods y muestra los registros de uno",
  pr=("La unidad más pequeña de Kubernetes es el ___. (3 letras)", "pod"),
  pr2=("La orden para ver los registros de un pod es kubectl ___. (4 letras)", "logs"),
  ec="guardar datos dentro de un pod creyendo que no desaparece", out="NAME                 READY   STATUS    RESTARTS   AGE\nmi-api-7d9f8-abcde   1/1     Running   0          2m"),
K("kubectl", d="la terminal de Kubernetes", u="crear, ver y cambiar todo lo que corre en el clúster",
  mas="kubectl apply -f archivo.yaml crea o actualiza recursos; get los lista, describe da detalles y delete los borra. kubectl port-forward abre un puerto del clúster en tu computador para probar.",
  k=["kubectl apply -f aplica un archivo YAML.", "kubectl describe muestra detalles de un recurso.", "kubectl port-forward abre un puerto local."],
  sit="Escribiste el archivo despliegue.yaml y quieres crear o actualizar esos recursos en el clúster. ¿Qué orden usas?",
  cod="""kubectl apply -f despliegue.yaml
kubectl get deployments""", h="aplica un archivo y lista los despliegues",
  pr=("La orden que crea o actualiza recursos desde un YAML es kubectl ___ -f. (5 letras)", "apply"),
  pr2=("La orden que muestra detalles de un recurso es kubectl ___. (8 letras)", "describe"),
  ec="crear recursos a mano con órdenes sueltas y no guardar el YAML en Git", out="deployment.apps/mi-api created"),
K("Deployment y Service", d="recursos de Kubernetes para mantener réplicas y darles una dirección fija", u="publicar tu app con varias copias y un punto de acceso estable",
  mas="Un Deployment dice qué imagen y cuántas réplicas quieres; Kubernetes las mantiene y actualiza poco a poco (rolling update). Un Service da un nombre y una IP fija para llegar a esos pods, y un Ingress los expone con un dominio.",
  k=["Un Deployment mantiene el número de réplicas.", "Un Service da una dirección fija a los pods.", "Un Ingress expone servicios con un dominio."],
  sit="Quieres 3 copias de tu API y un solo nombre estable para llegar a ellas dentro del clúster. ¿Qué dos recursos creas?",
  cod="""apiVersion: apps/v1
kind: Deployment
metadata: { name: mi-api }
spec:
  replicas: 3
  selector: { matchLabels: { app: mi-api } }
  template:
    metadata: { labels: { app: mi-api } }
    spec: { containers: [{ name: api, image: ana/mi-api:1.0 }] }""", h="un Deployment con tres réplicas",
  pr=("El recurso que mantiene las réplicas es el ___. (10 letras)", "deployment"),
  pr2=("La actualización gradual de pods se llama rolling ___. (6 letras)", "update"),
  ec="usar la etiqueta latest y no saber qué versión está corriendo", out=""),
K("CI con Docker", d="construir y publicar la imagen automáticamente en cada cambio", u="que siempre haya una imagen lista y probada en el registro",
  mas="En GitHub Actions, docker/build-push-action construye la imagen y la sube a Docker Hub o GitHub Container Registry (ghcr.io) en cada push a main. La etiqueta suele ser la versión o el hash del commit.",
  k=["CI puede construir la imagen en cada push.", "ghcr.io es el registro de contenedores de GitHub.", "Las imágenes se etiquetan con la versión o el hash."],
  sit="Quieres que cada vez que haces push a main se construya y publique la imagen de tu app sin hacerlo a mano. ¿Qué configuras?",
  cod="""- uses: docker/build-push-action@v6
  with:
    push: true
    tags: ghcr.io/ana/mi-api:${{ github.sha }}""", h="un paso de GitHub Actions que construye y sube la imagen",
  pr=("El registro de contenedores de GitHub es ___.io. (4 letras)", "ghcr"),
  pr2=("La acción oficial que construye y sube imágenes es docker/build-___-action. (4 letras)", "push"),
  ec="guardar la contraseña del registro en el YAML en lugar de un secreto", out=""),
K("Desplegar contenedores en la nube", d="publicar tu imagen en un servicio que la ejecuta por ti", u="que tu app tenga una URL pública sin administrar servidores",
  mas="Render, Railway, Fly.io, Google Cloud Run o Azure Container Apps toman tu Dockerfile o tu imagen y la ejecutan con HTTPS. Lee el puerto de la variable PORT y guarda las claves como variables de entorno del servicio.",
  k=["Cloud Run ejecuta contenedores sin administrar servidores.", "En la nube, el puerto suele venir en la variable PORT.", "Las claves se guardan como variables del servicio."],
  sit="Tu app ya tiene Dockerfile y quieres publicarla con una URL HTTPS sin configurar un servidor propio. ¿Qué tipo de servicio usas?",
  cod="""gcloud run deploy mi-api --source . --region us-central1""", h="despliega el proyecto en Google Cloud Run",
  pr=("En la nube, el puerto de la app suele venir en la variable ___. (4 letras)", "port"),
  pr2=("El servicio de Google que ejecuta contenedores sin servidores es Cloud ___. (3 letras)", "run"),
  ec="dejar el puerto fijo en el código y que el despliegue falle", out="Service URL: https://mi-api-abc123-uc.a.run.app"),
]
