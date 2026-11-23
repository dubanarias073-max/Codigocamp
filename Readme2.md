# CódigoCamp: guía de despliegue en la máquina virtual (DataSENA) con túnel de Tailscale

Esta guía instala **CódigoCamp** en la máquina virtual `10.12.19.82` (usuario `sofianieto`). La base de datos MySQL va en Docker y el enlace público sale por Tailscale. La máquina puede tener **otros proyectos, contenedores y bases de datos**. Cada paso que puede afectarlos tiene su advertencia ⚠️.

| Parte | CódigoCamp |
|---|---|
| Backend | Flask con Gunicorn en `127.0.0.1:5000`. También sirve el frontend |
| Base de datos | `codigocamp` en MySQL (Docker): en `mi-mysql` recreado **(opción A)** o en su propio contenedor `codigocamp-mysql` **(opción B)** |
| Clave de `root` de MySQL | `12345` |
| Enlace público | `https://codigocamp.taila41f89.ts.net` **(túnel con nombre propio)** o `https://<NOMBRE_DE_LA_MAQUINA>.taila41f89.ts.net:8443` **(túnel rápido)** |

> 🔐 **Sobre la clave `12345`:** es fácil de adivinar. Aquí solo es aceptable porque MySQL queda abierto **únicamente dentro de la máquina virtual** (`127.0.0.1`) y CódigoCamp no entra como `root`, sino con su propio usuario. No publiques el puerto de MySQL hacia la red con esta clave.
>
> Las demás claves aparecen como `<ASÍ>`. Reemplázalas por las tuyas y **no subas `backend/.env` a GitHub**.

## Antes de empezar: qué puede afectar a otros proyectos

| Paso | ¿Afecta a otros? | Detalle |
|---|---|---|
| 3. Opción A | ⚠️ **Sí, mucho** | Borra el contenedor `mi-mysql` y **todas** sus bases. Cambia la clave de `root` a `12345` |
| 3. Opción B | No | Contenedor, volumen y puerto (`3307`) nuevos |
| 4. Backend | Solo si el puerto `5000` está ocupado | Revisa los puertos en el paso 1 |
| 5. Servicio systemd | No | Servicio nuevo `codigocamp` |
| 6.1 Túnel rápido | ⚠️ Puede | Usa el puerto `8443` del Tailscale de la máquina. Si otro proyecto ya lo usa, lo reemplaza |
| 6.2 Túnel propio | No | Una segunda «máquina» de Tailscale en Docker |
| 6.2.5 Access controls | ⚠️ Puede | Las reglas de Tailscale aplican a **todas** las máquinas de la cuenta |
| 6.3 Google Cloud | ⚠️ Puede | Si el ID de cliente lo comparten otros proyectos, no borres sus direcciones |

---

## 1. Entrar a la máquina virtual

1. Abre **Citrix Secure Access** y habilita **Acceso de red** (sin esto, `10.12.19.82` no responde).
2. En VS Code instala la extensión **Remote - SSH** y entra con **`><` → Connect to Host… → `sofianieto@10.12.19.82`**.
3. Abre una terminal (**Terminal → New Terminal**). Todos los comandos de esta guía se ejecutan ahí, dentro de la máquina virtual.

Mira qué hay corriendo antes de tocar nada:

```bash
# Puertos que va a usar CódigoCamp
sudo ss -ltnp | grep -E ':(3306|3307|5000|8443)\b'

# Contenedores que ya existen (los de otros proyectos también)
sudo docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}'

# Túneles de Tailscale que ya están publicados
sudo tailscale funnel status
```

- Si el `5000` está ocupado, usa otro puerto (por ejemplo `5050`) en **todos** los pasos: servicio (5), túnel (6) y `.env` (4.2).
- Si el `3307` está ocupado y vas a usar la opción B, usa otro (por ejemplo `3308`).
- Anota qué contenedores y túneles existen. Así sabes qué no debes tocar.

---

## 2. Traer el proyecto

### Opción 1: desde GitHub

```bash
cd ~
git clone https://github.com/dubanarias073-max/Codigocamp.git
cd ~/Codigocamp
```

### Opción 2: subir el ZIP desde tu PC

En **PowerShell de tu PC** (con Citrix conectado):

```powershell
scp .\Codigocamp.zip sofianieto@10.12.19.82:~/
```

Luego, en la máquina virtual:

```bash
sudo apt install -y unzip
cd ~ && unzip -o Codigocamp.zip && cd ~/Codigocamp
```

> ⚠️ `unzip -o` sobrescribe sin preguntar. Si ya existe `~/Codigocamp` con un `backend/.env` tuyo, cópialo antes: `cp ~/Codigocamp/backend/.env ~/codigocamp.env`.

---

## 3. Base de datos

Elige **una** opción:

| | Opción A | Opción B (recomendada si hay otros proyectos) |
|---|---|---|
| Contenedor | `mi-mysql`, borrado y creado de nuevo | `codigocamp-mysql` (nuevo, solo para CódigoCamp) |
| Puerto | `3306` | `3307` |
| Bases dentro | `codigocamp` y las que vuelvas a cargar | solo `codigocamp` |
| Clave de `root` | `12345` | `12345` |
| Usuario de CódigoCamp | `codigocamp` | `codigocamp` |
| ¿Se pierde algo? | ⚠️ **Sí: todo lo que había en `mi-mysql`** | No, nada existente se toca |

---




#### B.1 Crear el volumen y el contenedor

```bash
sudo docker rm -f codigocamp-mysql ( "borra el contenedor incluido base de datos ")

sudo docker volume rm codigocamp-mysql-datos("borra el volumen tambien")


("crear contenedor y volumen")

sudo docker run --name codigocamp-mysql --restart unless-stopped \
  -e MYSQL_ROOT_PASSWORD='12345' \
  -e MYSQL_DATABASE=codigocamp \
  -e MYSQL_USER=codigocamp \
  -e MYSQL_PASSWORD='12345' \
  -p 127.0.0.1:3307:3306 \
  -v codigocamp-mysql-datos:/var/lib/mysql \
  -d mysql:8.4 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```

- `MYSQL_USER` y `MYSQL_PASSWORD` crean solos el usuario `codigocamp`, con permisos solo sobre la base `codigocamp`.
- `-p 127.0.0.1:3307:3306` deja MySQL abierto solo dentro de la máquina virtual.

> ⚠️ Si el puerto `3307` ya está ocupado (paso 1), Docker da error `port is already allocated`. Usa otro, por ejemplo `-p 127.0.0.1:3308:3306`, y pon ese mismo número en `DB_PORT` del `.env`.

#### B.2 Esperar a que MySQL termine de arrancar (unos 30 segundos)

```bash
until sudo docker exec codigocamp-mysql mysqladmin ping -u root -p'12345' --silent; do sleep 3; done; echo "MySQL listo"
```

#### B.3 Cargar las tablas de CódigoCamp

```bash
cd ~/Codigocamp
sudo docker exec -i codigocamp-mysql mysql -u root -p'12345' < "base de datos/codigocamp.sql"
```

#### B.4 Encender, apagar o ver el contenedor

```bash
sudo docker ps --filter name=codigocamp-mysql     # ¿está encendido? (Up)
sudo docker start codigocamp-mysql                 # encenderlo
sudo docker stop codigocamp-mysql                  # apagarlo (los datos se conservan)
```

> ⚠️ No uses `sudo docker volume prune` ni `sudo docker system prune --volumes`. Borran **todos** los volúmenes sin usar de la máquina, también los de otros proyectos.

---

### 3.C Comprobar la base

```bash
sudo docker exec -i codigocamp-mysql mysql -u codigocamp -p'12345' -e "USE codigocamp; SHOW TABLES;"
```

Deben aparecer unas 30 tablas (`usuarios`, `cursos`, `niveles`, `sesiones`…). Si sale `Empty set`, repite la carga (A.3 o B.3).

---

## 4. Backend (Flask)

### 4.1 Entorno virtual y dependencias

```bash
cd ~/Codigocamp/backend
sudo apt install -y python3-venv python3-pip     # solo la primera vez
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn
```

El entorno `venv` es solo de CódigoCamp: no cambia los paquetes de Python de otros proyectos.

### 4.2 Crear el archivo `.env`

Genera una clave secreta aleatoria y cópiala:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Crea `backend/.env`:

```bash
nano .env
```

Pega esto y cambia lo que está entre `< >`:

```env
# --- Producción ---
DEBUG=0
SECRET_KEY="12345"
# Va detrás del túnel de Tailscale: así cada persona tiene su propia IP
PROXY_CONFIABLE=1
# Trabajo no abre bases de datos de la máquina virtual (seguridad)
BD_EXTERNAS=0

# --- Base de datos ---
DB_HOST=127.0.0.1
# opción B (codigocamp-mysql) = 3307
DB_PORT=3307
DB_NAME=codigocamp
DB_USER=codigocamp
DB_PASSWORD="123456"

# --- Direcciones del proyecto: el túnel (sección 6) y localhost, separadas por coma ---
# CódigoCamp usa la misma por la que entró cada persona. La primera va en los avisos automáticos de racha.
APP_URL="https://codigocamp.taila41f89.ts.net,http://localhost:5000"
GOOGLE_REDIRECT_URI="https://codigocamp.taila41f89.ts.net/auth/google/callback/,http://localhost:5000/auth/google/callback/"

# --- IA ---
GEMINI_API_KEY="<TU_API_KEY_DE_GEMINI>"
GEMINI_MODEL=gemini-3.5-flash-lite

# --- Correo (Gmail con contraseña de aplicación) ---
SMTP_PORT="587"
SMTP_USERNAME="finanbot.sena@gmail.com"
SMTP_APP_PASSWORD="<contraseña de aplicación de Gmail>"
SMTP_FROM="finanbot.sena@gmail.com"

# --- Iniciar sesión con Google (opcional) ---
GOOGLE_CLIENT_ID="<ID_DE_CLIENTE>.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="<SECRETO_DE_CLIENTE>"

# --- Iniciar sesión con GitHub para git push en Trabajo (opcional; Readme.md sección 6.1) ---
GITHUB_CLIENT_ID="<CLIENT_ID_DE_LA_OAUTH_APP>"
GITHUB_CLIENT_SECRET="<CLIENT_SECRET>"
GITHUB_REDIRECT_URI="https://codigocamp.taila41f89.ts.net/auth/github/callback/"

# Direcciones del proyecto: localhost y el túnel, separadas por coma.
# CódigoCamp usa la misma por la que entró cada persona (la primera, en los avisos automáticos).
APP_URL="https://codigocamp.taila41f89.ts.net,http://localhost:5000"
GOOGLE_REDIRECT_URI="http://localhost:5000/auth/google/callback/,https://codigocamp.taila41f89.ts.net/auth/google/callback/"
```

Guarda con `Ctrl+O`, `Enter` y sal con `Ctrl+X`. Luego protege el archivo para que solo tu usuario lo lea:

```bash
chmod 600 .env
```

> Si usas el **túnel rápido** (6.1), cambia `https://codigocamp.taila41f89.ts.net` por `https://<NOMBRE_DE_LA_MAQUINA>.taila41f89.ts.net:8443` en las dos líneas.
>
> **`localhost` también funciona desde tu PC:** VS Code, conectado por SSH, reenvía el puerto 5000 de la máquina virtual (pestaña **Ports**). Así puedes abrir `http://localhost:5000` en tu navegador para probar sin el túnel.
>
> ⚠️ Si otro proyecto usa la **misma cuenta de Gmail** para enviar correos, compartís el límite diario de Gmail (unos 500 correos al día). Si uno lo agota, el otro tampoco puede enviar.

### 4.3 Cargar los cursos y comprobar todo

```bash
flask --app app check-retos         # revisa el contenido
flask --app app seed-retos          # carga los 23 cursos (tarda ~1 minuto)
flask --app app probar-correo finanbot.sena@gmail.com
flask --app app probar-ia
```

### 4.4 Probar que arranca

```bash
flask --app app run --host 127.0.0.1 --port 5000
```

En otra terminal de la máquina virtual:

```bash
curl -I http://127.0.0.1:5000/
```

Debe responder `HTTP/1.1 200 OK`. Detén la prueba con `Ctrl+C`.

---

## 5. Dejarlo encendido siempre (servicio de systemd)

Así CódigoCamp sigue funcionando aunque cierres VS Code o la sesión SSH, y arranca solo si se reinicia la máquina.

### 5.1 Crear el servicio

```bash
sudo nano /etc/systemd/system/codigocamp.service
```

> ⚠️ Usa exactamente el nombre `codigocamp.service`. Si escribes el nombre del servicio de otro proyecto, lo reemplazas.

Pega esto:

```ini
[Unit]
Description=CodigoCamp (Flask + Gunicorn)
After=network-online.target docker.service
Wants=network-online.target

[Service]
User=sofianieto
WorkingDirectory=/home/sofianieto/Codigocamp/backend
ExecStart=/home/sofianieto/Codigocamp/backend/venv/bin/gunicorn -w 1 --threads 8 --timeout 180 -b 127.0.0.1:5000 "app:create_app()"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> El servicio no necesita cargar el `.env`: CódigoCamp lo lee solo desde `backend/.env`.
>
> **Un solo worker (`-w 1`)** es a propósito: los avisos de racha, los límites de intentos y las conexiones a bases de datos de Trabajo viven en la memoria del proceso. Los 8 hilos atienden a varias personas a la vez.

### 5.2 Activarlo

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now codigocamp
sudo systemctl status codigocamp      # debe decir "active (running)"
```

`daemon-reload` solo vuelve a leer los archivos de servicio. No reinicia los servicios de otros proyectos.

Comandos del día a día:

```bash
sudo systemctl restart codigocamp     # después de cambiar el .env o el código
sudo journalctl -u codigocamp -f      # ver los registros en vivo (Ctrl+C para salir)
```

---

## 6. Túnel público con Tailscale

Un túnel de **Tailscale Funnel** usa el **nombre de la máquina** y solo puede abrir los puertos **443, 8443 y 10000**. Si la máquina ya publica otro proyecto en el `443`, hay dos formas de abrir el túnel de CódigoCamp:

| | 6.1 Túnel rápido | 6.2 Túnel con nombre propio (recomendado) |
|---|---|---|
| Enlace | `https://<NOMBRE_DE_LA_MAQUINA>.taila41f89.ts.net:8443` | `https://codigocamp.taila41f89.ts.net` |
| Dificultad | Un comando | Un contenedor de Docker |
| ¿Afecta a otros túneles? | ⚠️ Solo si alguien ya usa el `8443` | No |
| Desventaja | El enlace lleva el nombre de la máquina y `:8443` | Hay que crear una clave en la consola de Tailscale |

Primero mira cómo está Tailscale en la máquina:

```bash
tailscale status | head -3          # nombre de esta máquina en Tailscale
sudo tailscale funnel status        # qué puertos ya están publicados
```

> ⚠️ **Nunca ejecutes `sudo tailscale funnel reset` ni `sudo tailscale serve reset`.** Borran **todos** los túneles de la máquina, también los de otros proyectos.

### 6.1 Túnel rápido: otro puerto en la misma máquina

> ⚠️ Si `funnel status` ya muestra algo en `:8443`, **no sigas**: ese puerto es de otro proyecto y este comando lo reemplazaría. Usa `--https=10000` (y cambia `:8443` por `:10000` en el enlace) o el túnel 6.2.

```bash
sudo tailscale funnel --bg --https=8443 5000
sudo tailscale funnel status
```

- `--bg` lo deja funcionando en segundo plano, también tras reiniciar.
- Los túneles que ya estaban en otros puertos (por ejemplo, el `443`) no cambian.
- Para quitar **solo** el de CódigoCamp: `sudo tailscale funnel --https=8443 off`.

Abre `https://<NOMBRE_DE_LA_MAQUINA>.taila41f89.ts.net:8443` (con el nombre que mostró `tailscale status`).

### 6.2 Túnel con nombre propio: `codigocamp.taila41f89.ts.net`

La idea es crear una **segunda «máquina» de Tailscale** dentro de un contenedor de Docker, llamada `codigocamp`. Esa máquina publica `http://127.0.0.1:5000` con su propio nombre y su propio `443`, sin chocar con los túneles que ya existen.

#### 6.2.1 Crear una clave de acceso en Tailscale

1. Entra a <https://login.tailscale.com/admin/settings/keys> con la **misma cuenta** que usa la máquina virtual (la de `tailscale status`).
2. Pulsa **Generate auth key…**.
3. Deja **Reusable** y **Ephemeral** apagados y pulsa **Generate key**.
4. Copia la clave (`tskey-auth-…`). Solo se muestra una vez.

> ⚠️ Antes, revisa en **Machines** que no exista ya una máquina llamada `codigocamp`. Si existe, Tailscale le pondrá a la nueva `codigocamp-1` y el enlace cambiará.

#### 6.2.2 Crear la configuración del túnel

```bash
mkdir -p ~/codigocamp-tunel
cat > ~/codigocamp-tunel/serve.json <<'EOF'
{
  "TCP": { "443": { "HTTPS": true } },
  "Web": {
    "${TS_CERT_DOMAIN}:443": {
      "Handlers": { "/": { "Proxy": "http://127.0.0.1:5000" } }
    }
  },
  "AllowFunnel": { "${TS_CERT_DOMAIN}:443": true }
}
EOF
```

`${TS_CERT_DOMAIN}` se deja tal cual: el contenedor lo cambia solo por `codigocamp.taila41f89.ts.net`.

#### 6.2.3 Levantar el contenedor del túnel

```bash
sudo docker run -d --name codigocamp-tunel --restart unless-stopped \
  --network host \
  -e TS_AUTHKEY='<tskey-auth-...>' \
  -e TS_HOSTNAME=codigocamp \
  -e TS_STATE_DIR=/var/lib/tailscale \
  -e TS_USERSPACE=true \
  -e TS_SERVE_CONFIG=/config/serve.json \
  -e TS_TAILSCALED_EXTRA_ARGS="--port=41642" \
  -v codigocamp-tunel-estado:/var/lib/tailscale \
  -v ~/codigocamp-tunel:/config:ro \
  tailscale/tailscale:latest
```

Qué hace cada parte:

- `--network host`: el contenedor ve el `127.0.0.1:5000` de la máquina virtual, donde está CódigoCamp.
- `TS_USERSPACE=true` y `--port=41642`: no choca con el Tailscale de la máquina, que usa la red del sistema y el puerto `41641`.
- El volumen `codigocamp-tunel-estado` guarda la sesión. La clave solo se usa la primera vez.

> ⚠️ Si otro contenedor de Tailscale ya usa el puerto `41642` (`sudo ss -lunp | grep 4164`), cambia a `--port=41643`.

#### 6.2.4 Comprobar

```bash
sudo docker logs --tail 30 codigocamp-tunel
sudo docker exec codigocamp-tunel tailscale --socket=/tmp/tailscaled.sock status
sudo docker exec codigocamp-tunel tailscale --socket=/tmp/tailscaled.sock funnel status
```

Abre `https://codigocamp.taila41f89.ts.net` desde el celular, con datos móviles, para comprobar que funciona desde internet. La primera vez puede tardar uno o dos minutos mientras se crea el certificado HTTPS.

#### 6.2.5 Dos ajustes en la consola de Tailscale

1. **Que no se venza:** en **Machines → codigocamp → ⋯ → Disable key expiry**. Si no, el túnel se cae a los 180 días. Este ajuste es solo de esa máquina.
2. **Si `funnel status` dice que Funnel no está permitido:** en **Access controls**, la regla de Funnel debe incluir esta máquina. Si la máquina virtual ya publica un túnel, lo normal es que ya exista una regla como esta:

```json
"nodeAttrs": [
  { "target": ["autogroup:member"], "attr": ["funnel"] }
]
```

> ⚠️ **Access controls aplica a toda la cuenta de Tailscale.** Agrega lo que falte sin borrar ni cambiar las reglas que ya están: si quitas una, otros túneles o máquinas pueden dejar de funcionar. Si el editor marca un error, no guardes.

### 6.3 Registrar las direcciones en Google y en CódigoCamp

1. En `backend/.env`, `APP_URL` y `GOOGLE_REDIRECT_URI` deben tener el túnel y `localhost` (sección 4.2). Luego reinicia: `sudo systemctl restart codigocamp`.
2. Para «Iniciar sesión con Google», en <https://console.cloud.google.com/apis/credentials>, abre tu **ID de cliente de OAuth** y **agrega**:

| Campo | Direcciones |
|---|---|
| Orígenes autorizados de JavaScript | `https://codigocamp.taila41f89.ts.net`<br>`http://localhost:5000` |
| URI de redireccionamiento autorizados | `https://codigocamp.taila41f89.ts.net/auth/google/callback/`<br>`http://localhost:5000/auth/google/callback/` |

Escríbelas exactamente así, con la barra `/` final en las de redirección. Con el túnel rápido (6.1), usa `https://<NOMBRE_DE_LA_MAQUINA>.taila41f89.ts.net:8443` en lugar de la del túnel. Google puede tardar unos minutos en aplicar los cambios.

> ⚠️ Si ese ID de cliente también lo usa otro proyecto, **no borres ni edites sus direcciones**: solo agrega las de CódigoCamp con **+ Agregar URI**. Lo más limpio es crear un **ID de cliente nuevo** solo para CódigoCamp.

---

## 7. Actualizar CódigoCamp

```bash
cp ~/Codigocamp/backend/.env ~/codigocamp.env   # por si el ZIP o el pull lo pisan
# Proyectos de Trabajo de todas las cuentas (NO están en MySQL): copia antes de actualizar
tar czf ~/almacen_archivos-$(date +%F).tar.gz -C ~/Codigocamp/backend almacen_archivos
cd ~/Codigocamp
git pull                                   # o vuelve a subir y descomprimir el ZIP
cd backend && source venv/bin/activate
pip install -r requirements.txt gunicorn
flask --app app sync-retos                 # cursos nuevos, sin perder el progreso
sudo systemctl restart codigocamp
```

Al arrancar, CódigoCamp crea solo las tablas y columnas nuevas de la base `codigocamp`. No borra datos ni toca otras bases.

> ⚠️ Nunca borres `~/Codigocamp` para «instalar limpio»: se perderían `backend/.env` y `backend/almacen_archivos` (los proyectos de Trabajo). Si tienes que hacerlo, restaura el respaldo: `tar xzf ~/almacen_archivos-AAAA-MM-DD.tar.gz -C ~/Codigocamp/backend`.

---

## 8. Solución de problemas

| Mensaje o síntoma | Causa probable | Solución |
|---|---|---|
| El enlace del túnel muestra **502** o no carga | CódigoCamp no está corriendo | `sudo systemctl status codigocamp` y `sudo journalctl -u codigocamp -n 50` |
| `Access denied for user 'codigocamp'` | Clave o permisos | Repite el paso A.4, o revisa `MYSQL_PASSWORD` en B.1. Revisa `DB_PASSWORD` y `DB_PORT` en `.env` |
| `Access denied for user 'root'` | La clave de root no es `12345` | En la opción A, el volumen `mi-mysql-datos` ya existía con otra clave (aviso de A.1). Usa la clave anterior |
| Otro proyecto dejó de conectarse a MySQL después de la opción A | Su base se borró o su clave de root ya no sirve | Paso A.5: carga su `.sql`, cambia su clave a `12345` o crea de nuevo su usuario |
| Otro proyecto dice `Table doesn't exist` | Su base quedó vacía tras la opción A | Paso A.5 |
| `'cryptography' package is required for sha256_password or caching_sha2_password` | Falta una dependencia de MySQL 8 | `source venv/bin/activate && pip install -r requirements.txt` |
| `Can't connect to MySQL server on '127.0.0.1'` | El contenedor está apagado o el puerto es otro | `sudo docker start mi-mysql` (o `codigocamp-mysql`) y revisa `DB_PORT` |
| `Unknown database 'codigocamp'` | No se cargó el esquema | Repite A.3 (o B.3) |
| `port is already allocated` | Otro contenedor usa ese puerto | Usa otro puerto (por ejemplo `3308`) y ponlo en `DB_PORT` |
| Entras, pero la página te vuelve a sacar al login | `DEBUG=0` exige HTTPS y estás entrando por `http://` | Entra siempre por el enlace `https://` del túnel |
| Google dice `redirect_uri_mismatch` | Esa dirección no está registrada en Google Cloud | Paso 6.3, con la barra `/` final incluida, y la misma dirección en `GOOGLE_REDIRECT_URI` |
| Los correos tienen enlaces a `127.0.0.1` | `APP_URL` no se cambió | Pon el túnel y `localhost` en `APP_URL` (sección 4.2) y reinicia el servicio |
| `Address already in use` (puerto 5000) | Otro programa usa el puerto | `sudo ss -ltnp \| grep :5000`. Usa otro puerto en el servicio y en el túnel |
| El túnel de otro proyecto dejó de funcionar | Se usó su mismo puerto en 6.1, o se cambiaron las reglas de Tailscale | `sudo tailscale funnel status`. Quita el de CódigoCamp (`sudo tailscale funnel --https=8443 off`), vuelve a abrir el del otro proyecto y usa el túnel 6.2 |
| El túnel 6.2 no aparece en Tailscale | La clave venció o ya se usó | Crea otra clave, borra **solo** este contenedor y su volumen (`sudo docker rm -f codigocamp-tunel && sudo docker volume rm codigocamp-tunel-estado`) y repite el 6.2.3 |
| `Funnel not available` / `nodeAttr` | Funnel no está permitido para esa máquina | Paso 6.2.5 |
| Sin internet en tu PC al usar Citrix | La VPN manda todo el tráfico por la red del SENA | Cierra sesión en Citrix al terminar |

---

## 9. Resumen de comandos

```bash
# Estado de todo
sudo systemctl status codigocamp
sudo docker ps
sudo tailscale funnel status
sudo docker exec codigocamp-tunel tailscale --socket=/tmp/tailscaled.sock funnel status

# Reiniciar CódigoCamp (tras cambiar .env o el código)
sudo systemctl restart codigocamp

# Registros en vivo
sudo journalctl -u codigocamp -f

# Entrar a la base
sudo docker exec -it codigocamp-mysql mysql -u codigocamp -p codigocamp  
sudo docker exec -it codigocamp-mysql mysql -u root -p'12345'             # root
```

> ⚠️ Comandos que **nunca** debes usar en esta máquina porque afectan a otros proyectos: `sudo docker system prune`, `sudo docker volume prune`, `sudo docker rm -f $(sudo docker ps -aq)`, `sudo tailscale funnel reset`, `sudo tailscale serve reset`.

## 📱 App de Android (APK): CódigoCamp + widget

Desde la versión 0.6 hay **una sola app** (`apps/android`): abre CódigoCamp completo con su propia sesión e incluye el widget de racha.
El widget usa la sesión de la app, así que no se desconecta solo: solo deja de mostrar datos si cierras sesión.

### 1. Compilar el APK en GitHub Actions
1. (Una vez) En GitHub: **Settings → Secrets and variables → Actions → Variables → New variable**: `CODIGOCAMP_URL` = `https://codigocamp.taila41f89.ts.net` (la dirección que abre la app).
2. Sube los cambios (`git push`). El flujo **App de Android** (`.github/workflows/android.yml`) arranca solo; también con **Run workflow**.
3. Espera el ✅ (3 a 5 minutos), entra a la ejecución y descarga **`CodigoCamp-apk`** en *Artifacts*.
4. Descomprime el `.zip`: sale **`CodigoCamp.apk`**.

### 2. Subir el APK al servidor (VM)
```bash
mkdir -p ~/Codigocamp/frontend/descargas/          # en la VM, si no existe
scp CodigoCamp.apk sofianieto@10.12.19.82:~/Codigocamp/frontend/descargas/            # red local
scp CodigoCamp.apk sofianieto@<IP_TAILSCALE_VM>:~/Codigocamp/frontend/descargas/      # por Tailscale
rm -f ~/Codigocamp/frontend/descargas/CodigoCamp-Widget.apk                            # en la VM: el APK viejo ya no se usa
```
No hace falta reiniciar Flask. El botón **«Descargar la app para Android»** aparece en la portada (página de inicio) y en Configuración → App y widgets.

### 3. Instalar en el celular
1. Toca **«Descargar la app para Android»** y abre `CodigoCamp.apk` (permite instalar apps de esta fuente si Android lo pide).
2. Si tenías **«CódigoCamp Widget»** (la app vieja), desinstálala.
3. Abre **CódigoCamp** e inicia sesión.
4. Mantén pulsada la pantalla de inicio → **Widgets → CódigoCamp** y arrástralo.

## 🗄️ Consultas de la base de datos de CódigoCamp

Con la base ya creada, entra a MySQL (`sudo docker exec -it  codigocamp-mysql mysql -u root -p`) 

```sql
SHOW DATABASES;
```

```sql
USE codigocamp;
```

```sql
SHOW TABLES;
```

#### Cuentas

```sql
-- usuarios
SELECT * FROM usuarios;

SELECT id, email, nombre, creado_en
FROM usuarios
WHERE activo = 1
ORDER BY creado_en DESC;
```

#### Catalogo

```sql
-- cursos
SELECT * FROM cursos;

SELECT slug, nombre, tipo, color
FROM cursos
WHERE activo = 1
ORDER BY orden;

-- Cantidad de cursos por tipo
SELECT tipo, COUNT(*) AS total_cursos
FROM cursos
GROUP BY tipo;


-- etapas
SELECT * FROM etapas;

SELECT c.nombre AS curso, e.orden, e.titulo
FROM etapas e
JOIN cursos c ON c.id = e.curso_id
ORDER BY c.orden, e.orden;


-- secciones
SELECT * FROM secciones;

SELECT c.nombre AS curso, e.titulo AS etapa, s.orden, s.titulo AS seccion
FROM secciones s
JOIN etapas e ON e.id = s.etapa_id
JOIN cursos c ON c.id = e.curso_id
ORDER BY c.orden, e.orden, s.orden;


-- niveles
SELECT * FROM niveles;

SELECT c.nombre AS curso, s.titulo AS seccion, n.orden, n.titulo, n.tipo, n.xp
FROM niveles n
JOIN secciones s ON s.id = n.seccion_id
JOIN etapas e ON e.id = s.etapa_id
JOIN cursos c ON c.id = e.curso_id
ORDER BY c.orden, e.orden, s.orden, n.orden;

-- XP total disponible por curso
SELECT c.nombre AS curso, SUM(n.xp) AS xp_disponible
FROM niveles n
JOIN secciones s ON s.id = n.seccion_id
JOIN etapas e ON e.id = s.etapa_id
JOIN cursos c ON c.id = e.curso_id
GROUP BY c.id, c.nombre;


-- retos
SELECT * FROM retos;

SELECT n.titulo AS nivel, r.orden, r.tipo, r.enunciado, r.respuesta
FROM retos r
JOIN niveles n ON n.id = r.nivel_id
ORDER BY n.id, r.orden;

-- Cantidad de retos por tipo
SELECT tipo, COUNT(*) AS total
FROM retos
GROUP BY tipo
ORDER BY total DESC;

-- Cantidad de retos por curso
SELECT c.nombre AS curso, COUNT(r.id) AS total_retos
FROM cursos c
LEFT JOIN etapas e ON e.curso_id = c.id
LEFT JOIN secciones s ON s.etapa_id = e.id
LEFT JOIN niveles n ON n.seccion_id = s.id
LEFT JOIN retos r ON r.nivel_id = n.id
GROUP BY c.id, c.nombre
ORDER BY c.orden;
```

#### Perfil y progreso

```sql
-- perfiles
SELECT * FROM perfiles;

SELECT u.nombre, p.alias, p.codigo, c.nombre AS curso_actual,
       p.xp_total, p.vidas, p.racha_actual, p.racha_maxima
FROM perfiles p
JOIN usuarios u ON u.id = p.usuario_id
LEFT JOIN cursos c ON c.id = p.curso_actual_id
ORDER BY p.xp_total DESC;

-- Ranking top 10 por XP
SELECT COALESCE(p.alias, u.nombre) AS jugador, p.xp_total
FROM perfiles p
JOIN usuarios u ON u.id = p.usuario_id
ORDER BY p.xp_total DESC
LIMIT 10;

-- Usuarios que no completaron el onboarding
SELECT u.id, u.email
FROM perfiles p
JOIN usuarios u ON u.id = p.usuario_id
WHERE p.onboarding_completo = 0;


-- niveles_completados
SELECT * FROM niveles_completados;

SELECT u.nombre, n.titulo AS nivel, nc.estrellas, nc.veces, nc.completado_en
FROM niveles_completados nc
JOIN usuarios u ON u.id = nc.usuario_id
JOIN niveles n ON n.id = nc.nivel_id
ORDER BY nc.completado_en DESC;

-- Niveles completados y estrellas por usuario
SELECT u.nombre, COUNT(*) AS niveles_hechos, SUM(nc.estrellas) AS estrellas
FROM niveles_completados nc
JOIN usuarios u ON u.id = nc.usuario_id
GROUP BY u.id, u.nombre
ORDER BY niveles_hechos DESC;


-- lecciones_hechas
SELECT * FROM lecciones_hechas;

SELECT u.nombre, c.nombre AS curso, COUNT(*) AS lecciones
FROM lecciones_hechas lh
JOIN usuarios u ON u.id = lh.usuario_id
JOIN cursos c ON c.id = lh.curso_id
GROUP BY u.id, u.nombre, c.id, c.nombre
ORDER BY lecciones DESC;


-- actividad_diaria
SELECT * FROM actividad_diaria;

SELECT u.nombre, a.fecha, a.xp, a.niveles, a.perfectos
FROM actividad_diaria a
JOIN usuarios u ON u.id = a.usuario_id
ORDER BY a.fecha DESC;

-- XP de los ultimos 7 dias por usuario
SELECT u.nombre, SUM(a.xp) AS xp_semana
FROM actividad_diaria a
JOIN usuarios u ON u.id = a.usuario_id
WHERE a.fecha >= CURDATE() - INTERVAL 7 DAY
GROUP BY u.id, u.nombre
ORDER BY xp_semana DESC;


-- desafios_diarios
SELECT * FROM desafios_diarios;

SELECT clave, COUNT(*) AS veces_completado
FROM desafios_diarios
GROUP BY clave;

SELECT u.nombre, d.clave, d.fecha
FROM desafios_diarios d
JOIN usuarios u ON u.id = d.usuario_id
WHERE d.fecha = CURDATE();


-- puntos_desafio
SELECT * FROM puntos_desafio;

SELECT u.nombre, pd.mes, pd.puntos, pd.premio_dado
FROM puntos_desafio pd
JOIN usuarios u ON u.id = pd.usuario_id
ORDER BY pd.mes DESC, pd.puntos DESC;

-- Ranking del mes actual
SELECT u.nombre, pd.puntos
FROM puntos_desafio pd
JOIN usuarios u ON u.id = pd.usuario_id
WHERE pd.mes = DATE_FORMAT(CURDATE(), '%Y-%m-01')
ORDER BY pd.puntos DESC;
```

#### Tienda

```sql
-- articulos_tienda
SELECT * FROM articulos_tienda;

SELECT nombre, descripcion, precio, moneda
FROM articulos_tienda
WHERE activo = 1
ORDER BY orden;

-- Articulos agrupados por moneda
SELECT moneda, COUNT(*) AS articulos, MIN(precio) AS precio_min, MAX(precio) AS precio_max
FROM articulos_tienda
GROUP BY moneda;


-- compras
SELECT * FROM compras;

SELECT u.nombre, a.nombre AS articulo, c.precio, c.moneda, c.creada_en
FROM compras c
JOIN usuarios u ON u.id = c.usuario_id
JOIN articulos_tienda a ON a.id = c.articulo_id
ORDER BY c.creada_en DESC;

-- Articulos mas vendidos
SELECT a.nombre, COUNT(*) AS ventas, SUM(c.precio) AS total_gastado, c.moneda
FROM compras c
JOIN articulos_tienda a ON a.id = c.articulo_id
GROUP BY a.id, a.nombre, c.moneda
ORDER BY ventas DESC;
```

#### Social

```sql
-- amistades
SELECT * FROM amistades;

SELECT ud.nombre AS solicita, ua.nombre AS recibe, am.estado, am.creada_en
FROM amistades am
JOIN usuarios ud ON ud.id = am.de_usuario_id
JOIN usuarios ua ON ua.id = am.a_usuario_id
ORDER BY am.creada_en DESC;

-- Solicitudes pendientes
SELECT ud.nombre AS solicita, ua.nombre AS recibe
FROM amistades am
JOIN usuarios ud ON ud.id = am.de_usuario_id
JOIN usuarios ua ON ua.id = am.a_usuario_id
WHERE am.estado = 'pendiente';

-- Cantidad de amigos aceptados por usuario (en cualquier direccion)
SELECT u.nombre, COUNT(*) AS amigos
FROM usuarios u
JOIN amistades am
  ON (am.de_usuario_id = u.id OR am.a_usuario_id = u.id)
 AND am.estado = 'aceptada'
GROUP BY u.id, u.nombre
ORDER BY amigos DESC;


-- mensajes
SELECT * FROM mensajes;

SELECT m.id, ua.nombre AS autor, m.texto, m.leido, m.creado_en
FROM mensajes m
JOIN usuarios ua ON ua.id = m.autor_id
ORDER BY m.creado_en DESC;

-- Conversacion de una amistad (cambia el 1 por el id de la amistad)
SELECT u.nombre AS autor, m.texto, m.creado_en
FROM mensajes m
JOIN usuarios u ON u.id = m.autor_id
WHERE m.amistad_id = 1
ORDER BY m.creado_en;

-- Mensajes sin leer por amistad
SELECT amistad_id, COUNT(*) AS sin_leer
FROM mensajes
WHERE leido = 0
GROUP BY amistad_id;
```

#### Tutor ia

```sql
-- uso_tutor
SELECT * FROM uso_tutor;

-- Consultas al tutor por usuario (NULL = usuario eliminado)
SELECT COALESCE(u.nombre, '(eliminado)') AS usuario, COUNT(*) AS consultas
FROM uso_tutor t
LEFT JOIN usuarios u ON u.id = t.usuario_id
GROUP BY t.usuario_id, u.nombre
ORDER BY consultas DESC;

-- Consultas de las ultimas 24 horas por IP (control de limite de uso)
SELECT ip, COUNT(*) AS consultas
FROM uso_tutor
WHERE creado_en >= NOW() - INTERVAL 1 DAY
GROUP BY ip
ORDER BY consultas DESC;
```

#### Resumen general

```sql
-- Cantidad de filas en cada tabla
SELECT 'usuarios' AS tabla, COUNT(*) AS filas FROM usuarios
UNION ALL SELECT 'cursos', COUNT(*) FROM cursos
UNION ALL SELECT 'etapas', COUNT(*) FROM etapas
UNION ALL SELECT 'secciones', COUNT(*) FROM secciones
UNION ALL SELECT 'niveles', COUNT(*) FROM niveles
UNION ALL SELECT 'retos', COUNT(*) FROM retos
UNION ALL SELECT 'perfiles', COUNT(*) FROM perfiles
UNION ALL SELECT 'niveles_completados', COUNT(*) FROM niveles_completados
UNION ALL SELECT 'lecciones_hechas', COUNT(*) FROM lecciones_hechas
UNION ALL SELECT 'actividad_diaria', COUNT(*) FROM actividad_diaria
UNION ALL SELECT 'desafios_diarios', COUNT(*) FROM desafios_diarios
UNION ALL SELECT 'puntos_desafio', COUNT(*) FROM puntos_desafio
UNION ALL SELECT 'articulos_tienda', COUNT(*) FROM articulos_tienda
UNION ALL SELECT 'compras', COUNT(*) FROM compras
UNION ALL SELECT 'amistades', COUNT(*) FROM amistades
UNION ALL SELECT 'mensajes', COUNT(*) FROM mensajes
UNION ALL SELECT 'uso_tutor', COUNT(*) FROM uso_tutor;
```

#### Conector (terminal en el equipo del estudiante)

```sql
-- conectores
SELECT * FROM conectores;

-- Equipos conectados por cada estudiante (y cuándo se usaron por última vez)
SELECT u.nombre, c.equipo, c.sistema, c.carpeta, c.creado, c.ultimo
FROM conectores c
JOIN usuarios u ON u.id = c.usuario_id
ORDER BY c.ultimo DESC;

-- Cuántos equipos conectó cada sistema operativo
SELECT sistema, COUNT(*) AS equipos
FROM conectores
GROUP BY sistema
ORDER BY equipos DESC;
```

## Seguridad (Conector, enlaces, archivos y GitHub)

- **Conector:** pide el PIN, huella o clave del propio computador/celular antes de vincular; se cierra tras 30 min sin uso; bloquea comandos destructivos y comandos con enlaces peligrosos (servidor y programa).
- **Enlaces:** los de virus/estafa no se abren aunque el usuario acepte; los dudosos piden confirmación. Nada se guarda (solo caché en memoria). Opcional: `SAFE_BROWSING_KEY`; listas públicas con `flask --app app actualizar-listas` (diario).
- **Archivos:** antivirus propio + ClamAV si está instalado (`sudo apt install clamav clamav-daemon && sudo freshclam`). `ANTIVIRUS=0` lo apaga.
- **GitHub:** «Recordar» se mantiene; aviso al cerrar la ventana con la sesión activa.
- **Cabeceras:** CSP estricta en páginas normales, Referrer-Policy, Permissions-Policy y HSTS con HTTPS.
