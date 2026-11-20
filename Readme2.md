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
sudo docker exec -it mi-mysql mysql -u codigocamp -p codigocamp          # opción A
sudo docker exec -it codigocamp-mysql mysql -u codigocamp -p codigocamp  # opción B
sudo docker exec -it mi-mysql mysql -u root -p'12345'                     # root, opción A
sudo docker exec -it codigocamp-mysql mysql -u root -p'12345'             # root, opción B
```

> ⚠️ Comandos que **nunca** debes usar en esta máquina porque afectan a otros proyectos: `sudo docker system prune`, `sudo docker volume prune`, `sudo docker rm -f $(sudo docker ps -aq)`, `sudo tailscale funnel reset`, `sudo tailscale serve reset`.

## 📱 Despliegue del Widget de Android (APK)

El botón **«App del widget para Android (APK)»** en la sección de Configuración aparece automáticamente cuando el archivo compilado existe en la ruta `frontend/descargas/` del servidor.

### 1. Compilar el APK en GitHub Actions
1. Asegúrate de tener actualizado el archivo `.github/workflows/android-widget.yml` en la rama principal.
2. Ve a la pestaña **Actions** del repositorio en GitHub y selecciona el flujo **Widget de Android**.
3. Espera a que la ejecución finalice correctamente (**✅**, tarda entre 3 y 5 minutos).
4. Entra a la ejecución completada, baja hasta la sección **Artifacts** y descarga **`CodigoCamp-Widget-apk`**.
5. Descomprime el archivo `.zip` para obtener **`CodigoCamp-Widget.apk`**.

### 2. Subir el APK al servidor (VM)
Abre una terminal en la carpeta donde descomprimiste el archivo y transfiérelo a la máquina virtual mediante `scp`:

* **Desde la red local:**
  ```bash
  scp CodigoCamp-Widget.apk sofianieto@10.12.19.82:~/Codigocamp/frontend/descargas/
  ```

* **Desde fuera de la red (usando Tailscale):**
  ```bash
  scp CodigoCamp-Widget.apk sofianieto@<IP_TAILSCALE_VM>:~/Codigocamp/frontend/descargas/
  ```

> **Nota:** Si la carpeta destino no existe en la VM, créala previamente ejecutando `mkdir -p ~/Codigocamp/frontend/descargas/`. No es necesario reiniciar Flask después de subir el archivo.

### 3. Instalación y vinculación en Android
1. En el celular, abre **CódigoCamp → Configuración → App y widgets**.
2. Toca el botón **«App del widget para Android (APK)»**, descarga e instala la aplicación (autorizando la instalación desde fuentes externas si Android lo solicita).
3. Regresa a la misma pantalla con tu sesión iniciada y pulsa **🤖 Conectar widget de Android** para enlazar tu cuenta automáticamente.
4. Mantén presionada la pantalla de inicio del teléfono **→ Widgets → CódigoCamp** y arrástralo al escritorio.
