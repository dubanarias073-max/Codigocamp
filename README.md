# CódigoCamp

Plataforma para aprender a programar con un tutor de IA (Gemini): HTML y CSS desde cero, 13 lenguajes y bases de datos de todo tipo.

## Requisitos
- Node.js 20.6 o superior
- XAMPP con MySQL iniciado y MySQL Workbench
- Una clave de Gemini (https://aistudio.google.com/apikey)

## Puesta en marcha
1. Abre **XAMPP** e inicia **MySQL**.
2. En **Workbench**, conecta como `root` (sin contraseña, el valor por defecto de XAMPP) y ejecuta `sql/schema.sql`.
3. Copia `.env.example` a `.env` y completa `GEMINI_API_KEY` y `SESSION_SECRET`.
   No hace falta `DB_USER` ni `DB_PASSWORD`: por defecto entra como `root` sin contraseña.
4. En la terminal:
```bash
npm install
npm run dev
```
Abre http://localhost:3000

Genera un `SESSION_SECRET` con:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

## Páginas
| Archivo | Para qué sirve |
|---|---|
| `index.html` | Portada pública: características, cómo se usa y enlaces de acceso |
| `login.html` | Iniciar sesión (correo y contraseña) |
| `registro.html` | Crear cuenta (nombre, correo y contraseña repetida) |
| `inicio.html` | Panel del usuario: racha, XP, nivel y accesos a todo |
| `lenguajes.html` | 13 lenguajes × 5 lecciones, con laboratorio de JavaScript |
| `html-css.html` | Cursos de HTML y CSS desde cero, con laboratorio en vivo (`html-css.html#css` abre CSS) |
| `bases-de-datos.html` | 11 lecciones: SQL, MongoDB, Redis, Cassandra, Neo4j, series temporales, vectoriales |
| `retos.html` | Retos tipo Duolingo: XP, vidas, racha, estrellas y rutas Fácil, Medio y Difícil (pruebas de software) |
| `aprende.html` | Chat completo con el tutor de IA (la conversación se conserva al cambiar de página) |

Las páginas internas piden sesión o modo invitado; si no hay ninguno, llevan a `login.html`. Si ya hay sesión, `login.html` y `registro.html` llevan directamente a `inicio.html`.

## Retos
- Datos en `public/js/content/retos.js`: 3 rutas, 10 niveles, 50 preguntas.
- Tipos: opción, completar, encontrar el error, ordenar, **escribir código** (se ejecuta en un Web Worker con pruebas visibles y ocultas) y **cazar un bug** (escribe una entrada que haga fallar una función defectuosa).
- Vidas: 3 por nivel. Las preguntas falladas se repiten al final.
- XP: 10 por pregunta (15 las de código), +10 por nivel y +20 si no fallas ninguna. Racha: días seguidos con un nivel completado.
- El progreso se guarda en el navegador (localStorage), separado por usuario o invitado. Guardarlo en MySQL queda como siguiente paso.

## Estructura
- `public/` páginas, `css/` (`styles.css`, `portada.css`, `acceso.css`), `js/` y `img/` (logo)
- `public/js/acceso.js` lógica de `login.html` y `registro.html`
- `public/js/content/` lecciones y retos: `lenguajes.js`, `html.js`, `css.js`, `bd.js`, `retos.js`
- `server/` servidor Express, acceso (`auth/`), conexión a MySQL y llamada a Gemini (`gemini.js`)
- `sql/schema.sql` base de datos y tabla `usuarios`

## Logo y tema
- `public/img/logo.png`: tu logo original (archivo maestro).
- `public/img/logo-icon.png`: icono recortado para la cabecera. `favicon.png`: icono de la pestaña. `logo-hero.png`: versión de la portada.
- Si cambias el logo, vuelve a generar esas tres versiones a partir de `logo.png`.
- **Tema claro/oscuro:** botón ☀️/🌙 en la cabecera. Por defecto es oscuro y se recuerda la elección. Los colores están en las variables del inicio de `css/styles.css` (cian `#28f0e8` y verde `#68f890` del logo).

## Cuentas y modo invitado
- Registro e inicio de sesión con correo y contraseña (mínimo 8 caracteres). Las contraseñas de los usuarios se guardan cifradas (scrypt).
- Sesión: cookie HttpOnly firmada, dura 7 días.
- Invitado: 6 preguntas por minuto al tutor. Con cuenta: 20 por minuto.

## Seguridad
`root` sin contraseña es solo para desarrollo en tu equipo. Antes de publicar el sitio, crea un usuario de MySQL con contraseña y defínelo con `DB_USER` y `DB_PASSWORD`.
