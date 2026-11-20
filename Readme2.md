# Guía de Despliegue en Máquina Virtual (DataSENA) con Tailscale

Esta guía detalla cómo desplegar **CódigoCamp** en la máquina virtual `10.12.19.82` (usuario `sofianieto`), aislando su base de datos en **Docker**, programando **copias de seguridad automáticas** y publicando la aplicación con HTTPS mediante un túnel independiente de **Tailscale Funnel**.

| Componente | Configuración en Producción |
|---|---|
| **Backend + Frontend** | Flask con Gunicorn escuchando en `127.0.0.1:5000` (servicio `systemd`). |
| **Base de datos** | Contenedor `codigocamp-mysql` (MySQL 8.4) en `127.0.0.1:3307` *(Opción B recomendada)*. |
| **Respaldos automáticos** | Script diario con `cron` en `~/backups-codigocamp/` (retención de 7 días). |
| **Dominio público** | `https://codigocamp.taila41f89.ts.net` (contenedor aislado `codigocamp-tunel`). |

> ⚠️ **Importante:** Esta máquina virtual comparte recursos con otros proyectos (como `mi-mysql` en el puerto `3306` y otros túneles de Tailscale). Sigue estrictamente las instrucciones para no afectar servicios de terceros.

---

## 1. Conexión e inspección inicial

1. Conéctate a la VPN institucional mediante **Citrix Secure Access** (habilitando *Acceso de red*).
2. Abre VS Code con la extensión **Remote - SSH** y conéctate a `sofianieto@10.12.19.82`.
3. Abre una terminal y verifica qué puertos, contenedores y túneles están ocupados antes de instalar:

```bash
# Verificar puertos en uso
sudo ss -ltnp | grep -E ':(3306|3307|5000|8443)'

# Listar contenedores activos y detenidos
sudo docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}'

# Revisar túneles publicados en la máquina anfitriona
sudo tailscale funnel status
```

---

## 2. Descargar o actualizar el código

### Opción A: Clonar desde GitHub

```bash
cd ~
git clone https://github.com/dubanarias073-max/Codigocamp.git
cd ~/Codigocamp
```

### Opción B: Subir archivo ZIP desde tu equipo

Desde PowerShell en tu PC:

```powershell
scp .\Codigocamp.zip sofianieto@10.12.19.82:~/
```

Luego, en la máquina virtual:

```bash
sudo apt update && sudo apt install -y unzip
cd ~ && unzip -o Codigocamp.zip && cd ~/Codigocamp
```

*(Si ya tenías un archivo `backend/.env` configurado, respáldalo antes con `cp ~/Codigocamp/backend/.env ~/codigocamp.env`).*

---

## 3. Base de datos MySQL en Docker (Opción B — Aislada)

Para evitar borrar o alterar las bases de datos de otros compañeros en `mi-mysql` (puerto `3306`), crearemos un contenedor exclusivo llamado `codigocamp-mysql` en el puerto **`3307`**.

### 3.1 Crear volumen y levantar el contenedor

Reemplaza `<CLAVE_BD>` por la contraseña que usarás para el usuario `codigocamp` (por ejemplo, `12345` en entornos de prueba):

```bash
sudo docker volume create codigocamp-mysql-datos

sudo docker run -d --name codigocamp-mysql --restart unless-stopped \
  -e MYSQL_ROOT_PASSWORD='12345' \
  -e MYSQL_DATABASE=codigocamp \
  -e MYSQL_USER=codigocamp \
  -e MYSQL_PASSWORD='<CLAVE_BD>' \
  -p 127.0.0.1:3307:3306 \
  -v codigocamp-mysql-datos:/var/lib/mysql \
  mysql:8.4 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```

### 3.2 Esperar a que MySQL esté listo e importar el esquema

```bash
# Esperar arranque (~20-30 segundos)
until sudo docker exec codigocamp-mysql mysqladmin ping -u root -p'12345' --silent; do sleep 3; done; echo "MySQL listo"

# Importar tablas
cd ~/Codigocamp
sudo docker exec -i codigocamp-mysql mysql -u root -p'12345' < "base de datos/codigocamp.sql"
```

### 3.3 Asegurar permisos del usuario `codigocamp`

Docker conecta la aplicación a través de su puente de red interno (`172.17.0.1`). Ejecuta este comando para garantizar que el usuario `codigocamp` tenga acceso desde cualquier host (`'%'`):

```bash
sudo docker exec -i codigocamp-mysql mysql -u root -p'12345' -e "CREATE USER IF NOT EXISTS 'codigocamp'@'%' IDENTIFIED BY '<CLAVE_BD>'; ALTER USER 'codigocamp'@'%' IDENTIFIED BY '<CLAVE_BD>'; GRANT ALL PRIVILEGES ON codigocamp.* TO 'codigocamp'@'%'; FLUSH PRIVILEGES;"
```

### 3.4 Verificar tablas creadas

```bash
sudo docker exec -i codigocamp-mysql mysql -u root -p'12345' -e "USE codigocamp; SHOW TABLES;"
```

*(Deben listarse alrededor de 30 tablas).*

---

## 4. Respaldos automáticos de la base de datos y archivos

Para proteger el progreso de los estudiantes y los archivos subidos a la plataforma, configura un script diario de respaldo.

### 4.1 Crear el script de backup

```bash
mkdir -p ~/backups-codigocamp
cat > ~/backups-codigocamp/backup.sh <<'EOF'
#!/bin/bash
FECHA=$(date +"%Y-%m-%d_%H-%M")
DESTINO="$HOME/backups-codigocamp"

# 1. Volcado comprimido de MySQL (contenedor codigocamp-mysql)
sudo docker exec codigocamp-mysql mysqldump -u root -p'12345' --single-transaction codigocamp | gzip > "$DESTINO/codigocamp_bd_$FECHA.sql.gz"

# 2. Copia comprimida de archivos subidos y .env
tar -czf "$DESTINO/codigocamp_archivos_$FECHA.tar.gz" -C "$HOME/Codigocamp/backend" .env almacen_archivos 2>/dev/null || true

# 3. Eliminar respaldos con más de 7 días de antigüedad
find "$DESTINO" -type f -mtime +7 -delete
EOF

chmod +x ~/backups-codigocamp/backup.sh
```

### 4.2 Probar el script y programarlo con `cron`

1. Ejecuta una prueba manual para comprobar que crea los archivos `.gz`:
   ```bash
   ~/backups-codigocamp/backup.sh && ls -lh ~/backups-codigocamp/
   ```
2. Programa su ejecución automática todos los días a las **2:00 a. m.**:
   ```bash
   (crontab -l 2>/dev/null; echo "0 2 * * * /home/sofianieto/backups-codigocamp/backup.sh") | crontab -
   ```

### 4.3 Cómo restaurar un respaldo en caso de emergencia

```bash
gunzip -c ~/backups-codigocamp/codigocamp_bd_YYYY-MM-DD_HH-MM.sql.gz | sudo docker exec -i codigocamp-mysql mysql -u root -p'12345' codigocamp
```

---

## 5. Configuración del Backend (Flask)

### 5.1 Entorno virtual e instalación de paquetes

```bash
cd ~/Codigocamp/backend
sudo apt install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn
```

### 5.2 Configurar `backend/.env`

Genera una clave secreta segura:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Crea y edita el archivo `.env`:

```bash
nano .env
```

Pega la siguiente plantilla completando los valores entre `< >`:

```env
# --- Producción ---
DEBUG=0
SECRET_KEY="<CLAVE_ALEATORIA_GENERADA>"
PROXY_CONFIABLE=1
BD_EXTERNAS=0

# --- Base de datos (Contenedor aislado puerto 3307) ---
DB_HOST=127.0.0.1
DB_PORT=3307
DB_NAME=codigocamp
DB_USER=codigocamp
DB_PASSWORD="<CLAVE_BD>"

# --- URLs del proyecto ---
APP_URL="https://codigocamp.taila41f89.ts.net,http://localhost:5000"
GOOGLE_REDIRECT_URI="https://codigocamp.taila41f89.ts.net/auth/google/callback/,http://localhost:5000/auth/google/callback/"

# --- IA (Gemini) ---
GEMINI_API_KEY="<TU_API_KEY_DE_GEMINI>"
GEMINI_MODEL="gemini-3.5-flash-lite"

# --- Correo (Gmail SMTP) ---
SMTP_PORT="587"
SMTP_USERNAME="<tu_correo@gmail.com>"
SMTP_APP_PASSWORD="<contraseña_de_aplicación>"
SMTP_FROM="<tu_correo@gmail.com>"

# --- Google OAuth 2.0 ---
GOOGLE_CLIENT_ID="<TU_GOOGLE_CLIENT_ID>"
GOOGLE_CLIENT_SECRET="<TU_GOOGLE_CLIENT_SECRET>"
```

Guarda (`Ctrl+O`, `Enter`), sal (`Ctrl+X`) y restringe los permisos del archivo:

```bash
chmod 600 .env
```

### 5.3 Cargar cursos y verificar arranque

```bash
flask --app app check-retos
flask --app app seed-retos
flask --app app run --host 127.0.0.1 --port 5000
```

Comprueba en otra terminal con `curl -I http://127.0.0.1:5000/` que devuelva `HTTP/1.1 200 OK` y detén la prueba con `Ctrl+C`.

---

## 6. Servicio permanente con `systemd`

Crea el servicio para que CódigoCamp se ejecute en segundo plano y reinicie automáticamente:

```bash
sudo nano /etc/systemd/system/codigocamp.service
```

Contenido del archivo:

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

*(Se usa `-w 1` con 8 hilos para mantener sincronizados en memoria los temporizadores de racha y límites de peticiones).*

Activa el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now codigocamp
sudo systemctl status codigocamp
```

---

## 7. Túnel público aislado con Tailscale (Docker)

Para publicar CódigoCamp en **`https://codigocamp.taila41f89.ts.net`** sin interferir con el túnel principal de la máquina virtual, levantaremos un nodo independiente de Tailscale en Docker.

### 7.1 Generar Auth Key en Tailscale

1. Ingresa a [Tailscale Admin Console → Settings → Keys](https://login.tailscale.com/admin/settings/keys) con la cuenta asociada a la VM.
2. Verifica en **Machines** que no exista una máquina previa llamada `codigocamp` (si existe, elimínala antes).
3. Pulsa **Generate auth key…** (deja *Reusable* y *Ephemeral* desactivados) y copia la clave `tskey-auth-...`.

### 7.2 Crear configuración del túnel

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

### 7.3 Levantar el contenedor del túnel

Reemplaza `<TU_TS_AUTHKEY>` por la clave generada en el paso 7.1:

```bash
sudo docker run -d --name codigocamp-tunel --restart unless-stopped \
  --network host \
  -e TS_AUTHKEY='<TU_TS_AUTHKEY>' \
  -e TS_HOSTNAME=codigocamp \
  -e TS_STATE_DIR=/var/lib/tailscale \
  -e TS_USERSPACE=true \
  -e TS_SERVE_CONFIG=/config/serve.json \
  -e TS_TAILSCALED_EXTRA_ARGS="--port=41642" \
  -v codigocamp-tunel-estado:/var/lib/tailscale \
  -v ~/codigocamp-tunel:/config:ro \
  tailscale/tailscale:latest
```

### 7.4 Verificar estado y configurar Google Cloud

Espera ~15 segundos y comprueba que el certificado HTTPS y Funnel estén activos:

```bash
sudo docker exec codigocamp-tunel tailscale --socket=/tmp/tailscaled.sock status
sudo docker exec codigocamp-tunel tailscale --socket=/tmp/tailscaled.sock funnel status
```

1. En el panel web de Tailscale (**Machines → codigocamp → ⋯**), selecciona **Disable key expiry** para evitar que el túnel caduque a los 180 días.
2. Configura las URLs en [Google Cloud Console → Credenciales](https://console.cloud.google.com/apis/credentials):
   - **Orígenes de JavaScript:** `https://codigocamp.taila41f89.ts.net` y `http://localhost:5000`
   - **URIs de redireccionamiento:** `https://codigocamp.taila41f89.ts.net/auth/google/callback/` y `http://localhost:5000/auth/google/callback/`

---

## 8. Actualización continua

Cuando subas cambios nuevos al repositorio:

```bash
cp ~/Codigocamp/backend/.env ~/codigocamp.env
cd ~/Codigocamp
git pull
cd backend && source venv/bin/activate
pip install -r requirements.txt gunicorn
flask --app app sync-retos
sudo systemctl restart codigocamp
```

---

## 9. Comandos de mantenimiento y emergencias

```bash
# Ver estado de servicios y contenedores
sudo systemctl status codigocamp
sudo docker ps
sudo docker exec codigocamp-tunel tailscale --socket=/tmp/tailscaled.sock funnel status

# Ver logs de la aplicación en tiempo real
sudo journalctl -u codigocamp -f

# Reiniciar backend tras editar .env
sudo systemctl restart codigocamp

# Recrear solo el túnel de CódigoCamp si falla la clave
sudo docker rm -f codigocamp-tunel && sudo docker volume rm codigocamp-tunel-estado
```

> 🛑 **Comandos prohibidos en este servidor (afectan a otros proyectos):**
> - `sudo docker system prune` / `sudo docker volume prune`
> - `sudo tailscale funnel reset` / `sudo tailscale serve reset` *(si necesitas limpiar un túnel atascado en la máquina anfitriona sin tocar contenedores, usa `echo '{}' | sudo tailscale serve set-raw`)*.
