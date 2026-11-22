// Idioma de la interfaz (español / English). Se carga en el <head> de todas las páginas, antes que todo.
// Español es el idioma original: si el usuario elige inglés, este archivo traduce los textos de la interfaz
// (botones, menús, títulos, avisos, placeholders…) a medida que aparecen en la página.
// No se traducen: mensajes de los chats, respuestas de la IA, código ni el contenido de las lecciones.
// Para traducir un texto nuevo, agrégalo a D (texto exacto en español → inglés) o a PATRONES si lleva números.
(function () {
  "use strict";
  var idioma = "es";
  try { idioma = localStorage.getItem("cc_idioma") === "en" ? "en" : "es"; } catch (e) { /* sin almacenamiento */ }
  window.CC_IDIOMA = idioma;
  document.documentElement.lang = idioma;
  window.ccIdioma = function (nuevo) {
    try { localStorage.setItem("cc_idioma", nuevo === "en" ? "en" : "es"); } catch (e) { /* sin almacenamiento */ }
  };
  window.ccT = function (s) { return s; };

  // En las páginas públicas (portada, entrar, registrarse…) hay un botón para cambiar de idioma.
  if (/^\/(index\.html)?$|\/pages\/(login|registro|restablecer|onboarding)\.html$/.test(location.pathname)) {
    document.addEventListener("DOMContentLoaded", function () {
      var b = document.createElement("button");
      b.type = "button"; b.className = "cc-idioma-btn"; b.setAttribute("data-sin-traducir", "");
      b.textContent = idioma === "en" ? "🇪🇸 Español" : "🇺🇸 English";
      b.setAttribute("aria-label", idioma === "en" ? "Cambiar a español" : "Switch to English");
      b.style.cssText = "position:fixed;top:12px;right:12px;z-index:9999;padding:7px 12px;border-radius:999px;border:1px solid rgba(127,127,127,.4);background:rgba(20,20,30,.75);color:#fff;font:600 13px system-ui,sans-serif;cursor:pointer;backdrop-filter:blur(6px)";
      b.onclick = function () {
        window.ccIdioma(idioma === "en" ? "es" : "en");
        try { localStorage.setItem("cc_idioma_pendiente", "1"); } catch (e) { /* sin almacenamiento */ }   // al entrar se guarda en la cuenta
        location.reload();
      };
      document.body.appendChild(b);
    });
  }
  if (idioma !== "en") return;

  var D = {
    // Navegación y comunes
    "Inicio": "Home", "Aprende": "Learn", "Retos": "Challenges", "Trabajo": "Workspace", "Chats": "Chats", "IA": "AI",
    "Tienda": "Shop", "Recompensas": "Rewards", "Perfil": "Profile", "Configuración": "Settings", "Más": "More",
    "Principal": "Main", "Menú principal": "Main menu", "Menú principal móvil": "Mobile main menu",
    "Cargando…": "Loading…", "Guardar": "Save", "Cancelar": "Cancel", "Cerrar": "Close", "Copiar": "Copy", "Borrar": "Delete",
    "Eliminar": "Delete", "Editar": "Edit", "Aceptar": "OK", "Continuar": "Continue", "Volver": "Back", "Salir": "Exit",
    "Buscar": "Search", "Enviar": "Send", "Agregar": "Add", "Actualizar": "Refresh", "Abrir": "Open", "Leer": "Read",
    "Opciones": "Options", "Listo": "Done", "Sí": "Yes", "No": "No", "Ir": "Go", "Atrás": "Back", "Adelante": "Forward",
    "Renombrar": "Rename", "Fijar": "Pin", "Desfijar": "Unpin", "Quitar": "Remove", "Probar": "Try", "Comprar": "Buy",
    "Ponerme": "Equip", "Quitarme": "Unequip", "Puesto": "Equipped", "Ver todos →": "See all →", "Ir a la tienda →": "Go to the shop →",
    "Tu curso": "Your course", "Elige un curso en Configuración": "Choose a course in Settings", "Practicar": "Practice",
    "Ver desafíos": "See challenges", "Ir a la tienda": "Go to the shop", "Nivel": "Level", "día": "day", "días": "days",
    "de racha": "day streak", "Racha": "Streak", "Diamantes": "Diamonds", "Vidas": "Lives", "Cofres": "Chests", "Cursos": "Courses",
    "Etapas": "Stages", "Lección": "Lesson", "Lecciones": "Lessons", "Desafíos": "Challenges", "Logros": "Achievements",
    "Ya abriste este cofre.": "You already opened this chest.", "Completa la lección anterior primero.": "Finish the previous lesson first.",
    "Cofre de la sección": "Section chest", "Tu premio por llegar hasta aquí": "Your prize for getting this far",
    "¡Genial!": "Awesome!", "¡Listo!": "Done!", "No se pudo copiar": "Couldn't copy", "No se pudo cargar.": "Couldn't load.",
    "La IA puede equivocarse: revisa lo que te responde.": "AI can make mistakes: double-check its answers.",
    "🚫 Mensaje eliminado": "🚫 Message deleted", "Mensaje eliminado": "Message deleted",

    // Inicio
    "Mi curso": "My course", "Ver todas las etapas": "See all stages", "Etapas del curso": "Course stages", "Elige tu curso": "Choose your course",
    "Mis cursos": "My courses", "VER ETAPAS": "SEE STAGES", "Ir a las lecciones": "Go to the lessons",
    "Mientras tanto, estudia sus lecciones o prueba otro curso.": "Meanwhile, study its lessons or try another course.",
    "▶ EMPEZAR": "▶ START", "↺ PENDIENTE": "↺ PENDING", "🏋️ Práctica de repaso": "🏋️ Review practice", "🏆 Examen de la etapa": "🏆 Stage exam",
    "Calendario de racha": "Streak calendar", "Salvarrachas: protegen tu racha si un día no practicas": "Streak freezes: they protect your streak if you skip a day",
    "¡Practicaste hoy!": "You practiced today!", "¡Practica hoy para no perder tu racha!": "Practice today so you don't lose your streak!",
    "Empieza una racha hoy": "Start a streak today",

    // Configuración
    "Secciones de configuración": "Settings sections", "Cuenta": "Account", "Nombre, usuario e ID": "Name, username and ID",
    "Aprendizaje": "Learning", "Curso y meta diaria": "Course and daily goal", "Apariencia": "Appearance",
    "Tema, sonidos y cosméticos": "Theme, sounds and cosmetics", "Seguridad": "Security", "Contraseña y dispositivos": "Password and devices",
    "Correos": "Emails", "Alertas y avisos de racha": "Alerts and streak reminders", "App y widgets": "App and widgets",
    "Instalar en tus dispositivos": "Install on your devices", "Sesión": "Session", "Cerrar sesión": "Log out", "Nombre": "Name",
    "Nombre de usuario": "Username", "(para que tus amigos te encuentren; 3 a 20 letras, números o _)": "(so your friends can find you; 3 to 20 letters, numbers or _)",
    "Tu ID:": "Your ID:", "· Correo:": "· Email:", "Curso que estudias": "Course you're studying", "Meta diaria": "Daily goal",
    "5 minutos · relajado": "5 minutes · relaxed", "10 minutos · normal": "10 minutes · regular", "15 minutos · serio": "15 minutes · serious",
    "30 minutos · intenso": "30 minutes · intense", "Tema visual": "Visual theme", "Según tu dispositivo": "Match your device",
    "Claro": "Light", "Oscuro": "Dark", "Sonidos": "Sounds",
    "Al acertar o fallar, al terminar una lección, al hacer tu racha y al abrir cofres.": "When you get answers right or wrong, finish a lesson, extend your streak and open chests.",
    "Menos animaciones": "Fewer animations", "Quita fondos animados, efectos y la lluvia de código al cargar.": "Removes animated backgrounds, effects and the code rain while loading.",
    "Consigue fondos, punteros, temas, marcos y efectos en la tienda →": "Get backgrounds, pointers, themes, frames and effects in the shop →",
    "Quitar todos": "Remove all", "Idioma": "Language", "Idioma de la aplicación": "App language",
    "Los menús, botones y avisos cambian de idioma. Las lecciones y retos siguen en español.": "Menus, buttons and messages change language. Lessons and challenges stay in Spanish.",
    "Contraseña actual": "Current password", "Nueva contraseña": "New password", "(mínimo 6, con una mayúscula y un número)": "(at least 6, with an uppercase letter and a number)",
    "Repite la nueva": "Repeat the new one", "Cambiar contraseña": "Change password",
    "Te avisamos por correo cada vez que cambie tu contraseña o entres desde un dispositivo nuevo.": "We email you every time your password changes or you sign in from a new device.",
    "Dónde tienes la sesión abierta": "Where you're signed in",
    "Si no reconoces un dispositivo, ciérralo: queda fuera al instante (aunque tenga «recordarme»). Cambiar la contraseña también cierra los demás.": "If you don't recognize a device, sign it out: it's logged out instantly (even with “remember me”). Changing your password also signs out the others.",
    "Cerrar sesión en los demás dispositivos": "Log out of other devices", "Cerrar sesión en todos los dispositivos": "Log out of all devices",
    "Historial de dispositivos": "Device history", "Alertas de seguridad": "Security alerts",
    "Inicio de sesión en un dispositivo nuevo y cambio de contraseña. Recomendado. (El correo de bienvenida al registrarte siempre se envía.)": "Sign-in from a new device and password change. Recommended. (The welcome email is always sent when you sign up.)",
    "Avisos de racha": "Streak reminders",
    "Si un día se te olvida entrar, te avisamos por la tarde (6 p. m.) y otra vez en las últimas horas (9 p. m.) antes de perder tu racha.": "If you forget to come in one day, we remind you in the afternoon (6 p.m.) and again in the last hours (9 p.m.) before you lose your streak.",
    "Novedades de CódigoCamp": "CódigoCamp news", "Cursos nuevos y mejoras, muy de vez en cuando.": "New courses and improvements, once in a while.",
    "⬇️ Instalar CódigoCamp": "⬇️ Install CódigoCamp", "Windows 10 y 11": "Windows 10 and 11", "Abre CódigoCamp en": "Open CódigoCamp in",
    "Pulsa el botón": "Press the", "Instalar": "Install", "de esta página o el ícono ⊕ de la barra de direcciones.": "button on this page or the ⊕ icon in the address bar.",
    "Queda en el menú Inicio y la barra de tareas. En Windows 11 agrega el": "It goes to the Start menu and the taskbar. On Windows 11 add the",
    "widget de racha": "streak widget", ": tecla Windows + W → «+» → CódigoCamp.": ": Windows key + W → “+” → CódigoCamp.",
    "Safari 17 o más": "Safari 17 or newer", ": menú Archivo →": ": File menu →", "Agregar al Dock": "Add to Dock",
    ": ícono ⊕ de la barra de direcciones → Instalar.": ": ⊕ icon in the address bar → Install.", "La encuentras en Launchpad y en el Dock.": "You'll find it in Launchpad and the Dock.",
    "Pulsa": "Press", "aquí o el ícono ⊕ de la barra de direcciones.": "here or the ⊕ icon in the address bar.",
    "Aparece en el menú de aplicaciones con su propio ícono.": "It appears in the applications menu with its own icon.",
    "Descarga e instala la app": "Download and install the app",
    "(botón «Descargar la app para Android»; si no aparece, pídele el APK a quien administra CódigoCamp). Si Android pregunta, permite instalar apps de esta fuente.": "(“Download the Android app” button; if it doesn't show up, ask whoever runs CódigoCamp for the APK). If Android asks, allow installing apps from this source.",
    "Abre la app e inicia sesión. Es CódigoCamp completo, y el widget queda conectado solo a tu sesión de la app.": "Open the app and sign in. It's the full CódigoCamp, and the widget connects to your app session automatically.",
    "Mantén pulsada la pantalla de inicio →": "Long-press the home screen →",
    "y arrástralo. Se actualiza cada 30 minutos y cada vez que abres la app; tócalo para practicar.": "and drag it. It updates every 30 minutes and every time you open the app; tap it to practice.",
    "Si cierras sesión en la app (o desde otro dispositivo), el widget deja de mostrar tus datos hasta que vuelvas a entrar.": "If you log out of the app (or from another device), the widget stops showing your data until you sign in again.",
    "¿Tenías la app vieja «CódigoCamp Widget»? Desinstálala: ya no hace falta.": "Had the old “CódigoCamp Widget” app? Uninstall it: it's no longer needed.",
    "iPhone y iPad (iOS / iPadOS)": "iPhone and iPad (iOS / iPadOS)", "(en iOS 16.4+ también sirve Chrome o Edge).": "(on iOS 16.4+ Chrome or Edge also work).",
    "Compartir": "Share", "(el cuadro con la flecha ↑).": "(the box with the ↑ arrow).", "Elige": "Choose",
    "Agregar a pantalla de inicio": "Add to Home Screen", "→ Agregar.": "→ Add.", "Queda en el selector de apps y en la biblioteca.": "It goes to the launcher and the app library.",
    "Tu racha, la semana, la meta de hoy, vidas y diamantes en la pantalla de inicio o el escritorio, en cualquier sistema.": "Your streak, the week, today's goal, lives and diamonds on your home screen or desktop, on any system.",
    "Los widgets usan": "Widgets use", "tu sesión": "your session",
    ": no tienes que volver a entrar. Siguen funcionando hasta que tú cierres sesión (aquí o desde otro dispositivo).": ": you don't have to sign in again. They keep working until you log out (here or from another device).",
    "📌 Abrir widget flotante": "📌 Open floating widget", "⬇️ Widget para iPhone/iPad (Scriptable)": "⬇️ iPhone/iPad widget (Scriptable)",
    "🤖 Descargar la app para Android (incluye el widget)": "🤖 Download the Android app (includes the widget)", "🔗 Copiar enlace del widget": "🔗 Copy widget link",
    "Windows 11 y 10": "Windows 11 and 10", ": instala CódigoCamp (botón de arriba) con": ": install CódigoCamp (button above) with", ". Pulsa": ". Press",
    "y elige": "and choose", "Tu racha": "Your streak", "Meta de hoy": "Today's goal", "(o si no aparecen): pulsa": "(or if they don't show up): press",
    ": queda una ventanita siempre encima de las demás.": ": a small window stays on top of the others.", "En": "In", "Chrome o Edge": "Chrome or Edge",
    "→ en la ventana del widget pulsa 📌 otra vez: queda siempre encima.": "→ in the widget window press 📌 again: it stays on top.",
    "Chrome, Chromium o Edge": "Chrome, Chromium or Edge", "y pulsa": "and press", "; en el widget pulsa 📌 otra vez para dejarlo siempre encima.": "; in the widget press 📌 again to keep it on top.",
    "Instala la app": "Install the app", "Vuelve aquí (con tu sesión iniciada) y pulsa": "Come back here (signed in) and press",
    "🤖 Conectar widget de Android": "🤖 Connect Android widget", ": la app queda conectada a tu cuenta, sin escribir nada.": ": the app connects to your account without typing anything.",
    "y arrástralo. Se actualiza cada 30 minutos; tócalo para practicar.": "and drag it. It updates every 30 minutes; tap it to practice.",
    "iPhone y iPad": "iPhone and iPad", "Instala": "Install", "(gratis) desde la App Store.": "(free) from the App Store.",
    "Aquí (con tu sesión iniciada) pulsa": "Here (signed in) press", "⬇️ Widget para iPhone/iPad": "⬇️ iPhone/iPad widget", "→ se descarga": "→ it downloads",
    ", ya conectado a tu cuenta. Ábrelo con": ", already connected to your account. Open it with", "Compartir → Scriptable": "Share → Scriptable",
    "(o cópialo en un script nuevo de Scriptable).": "(or paste it into a new Scriptable script).", "→ elige el tamaño → toca el widget →": "→ choose the size → tap the widget →",
    ". En": ". In", "puedes escribir": "you can type", "calendario": "calendar", "También funciona en la": "It also works on the", "pantalla de bloqueo": "lock screen",
    "(iOS 16+): circular, rectangular o en línea.": "(iOS 16+): circular, rectangular or inline.",
    "En un Mac con chip Apple (M1 o más nuevo): instala": "On a Mac with Apple silicon (M1 or newer): install",
    "de la App Store y sigue los pasos de iPhone; el widget va en el escritorio o el Centro de notificaciones.": "from the App Store and follow the iPhone steps; the widget goes on the desktop or in Notification Center.",
    "Con macOS Sonoma o más nuevo, los widgets de tu iPhone (Scriptable) también se pueden poner en el escritorio del Mac.": "With macOS Sonoma or newer, your iPhone widgets (Scriptable) can also go on the Mac desktop.",
    "y fija la ventana donde quieras; queda siempre encima.": "and pin the window wherever you like; it stays on top.",
    "Sales en este dispositivo. Los demás siguen dentro.": "You're logged out on this device. The others stay signed in.",
    "Términos y condiciones": "Terms and conditions", "Lo que debes saber: copias de tus proyectos, IA, datos y reglas.": "What you should know: project backups, AI, data and rules.",
    "Cerrar sesión en otro dispositivo": "Log out of another device", "Elige cuál en Seguridad → Dónde tienes la sesión abierta.": "Choose which one in Security → Where you're signed in.",
    "Ver dispositivos": "See devices", "Sales en todos lados, incluido este. Tendrás que volver a entrar.": "You're logged out everywhere, including here. You'll have to sign in again.",
    "Cerrar en todos": "Log out everywhere", "Tus estadísticas": "Your stats", "ID copiado": "ID copied", "Cuenta guardada": "Account saved",
    "No se pudo guardar en este navegador.": "Couldn't save in this browser.", "Tema de color": "Color theme", "Cosméticos quitados": "Cosmetics removed",
    "Las contraseñas nuevas no coinciden.": "The new passwords don't match.",
    "Contraseña cambiada. Cerramos la sesión en tus otros dispositivos y te enviamos un correo de aviso.": "Password changed. We logged out your other devices and sent you an email.",
    "Último acceso": "Last access", "Sin registros todavía.": "No records yet.", "entró": "signed in", "No hay sesiones abiertas.": "No open sessions.",
    "¿Cerrar la sesión en este dispositivo?": "Log out on this device?", "¿Cerrar la sesión en ese dispositivo? Quedará fuera al instante.": "Log out that device? It will be signed out instantly.",
    "Listo: ese dispositivo ya no tiene tu sesión.": "Done: that device no longer has your session.",
    "¿Cerrar la sesión en todos los demás dispositivos? Este seguirá dentro.": "Log out of all other devices? This one stays signed in.",
    "¿Cerrar la sesión en TODOS los dispositivos, incluido este?": "Log out of ALL devices, including this one?",
    "✓ Ya estás usando la app instalada.": "✓ You're already using the installed app.", "✓ Estás en la app: el widget de Android ya usa esta sesión.": "✓ You're in the app: the Android widget already uses this session.",
    "Enlace del widget copiado": "Widget link copied", "Este dispositivo": "This device", "Fondo": "Background", "Puntero": "Pointer", "Tema": "Theme",
    "Marco": "Frame", "Efecto": "Effect", "Rastro": "Trail", "Ninguno": "None",

    // Tienda
    "Tu saldo de diamantes": "Your diamond balance", "Categorías de la tienda": "Shop categories", "Fondos": "Backgrounds", "Punteros": "Pointers",
    "Temas": "Themes", "Marcos": "Frames", "Efectos": "Effects", "Rastros": "Trails", "Potenciadores": "Power-ups", "Mi colección": "My collection",
    "¿Te faltan diamantes? Completa tus misiones →": "Need more diamonds? Complete your missions →", "Resultado de la compra": "Purchase result",
    "Común": "Common", "Raro": "Rare", "Épico": "Epic", "Legendario": "Legendary", "Mítico": "Mythic", "Exclusivo": "Exclusive",
    "El fondo se ve detrás de todas las páginas. Prueba cómo queda con «Probar».": "The background shows behind every page. See how it looks with “Try”.",
    "Cada puntero trae 3: normal, mano (enlaces y botones) y texto (para escribir). Pasa el mouse por cada uno para probarlo.": "Each pointer comes with 3: normal, hand (links and buttons) and text (for typing). Hover over each one to try it.",
    "Cambia el color de botones, barras y enlaces en todo CódigoCamp.": "Changes the color of buttons, bars and links across CódigoCamp.",
    "Un aro alrededor de tu foto de perfil: se ve en tu perfil, en los chats y en la barra lateral.": "A ring around your profile photo: it shows on your profile, in chats and in the sidebar.",
    "Haz clic en la vista previa para ver el efecto.": "Click the preview to see the effect.", "Vidas, salvarrachas, XP y cofres sorpresa.": "Lives, streak freezes, XP and mystery chests.",
    "Todo lo que tienes. Ponte o quítate cada cosmético cuando quieras. Los exclusivos salen de los cofres de Recompensas.": "Everything you own. Equip or remove each cosmetic whenever you want. Exclusives come from Rewards chests.",
    "Un rastro que sigue a tu mouse en la computadora y a tu dedo en el celular, también mientras haces scroll.": "A trail that follows your mouse on computers and your finger on phones, even while you scroll.",
    "En tu colección": "In your collection", "Solo en cofres": "Chests only", "te faltan": "you need", "Dejar de probar": "Stop trying",
    "Aún no tienes cosméticos. ¡Compra el primero o abre un cofre en Recompensas!": "You don't have cosmetics yet. Buy your first one or open a chest in Rewards!",
    "¡Listo! Ya lo tienes puesto en todo CódigoCamp.": "Done! It's now equipped across CódigoCamp.",
    "Vista previa: así se vería. Vuelve a pulsar para dejar de probar.": "Preview: this is how it would look. Press again to stop trying.",
    "¡Nuevo cosmético en tu colección!": "New cosmetic in your collection!", "¡Compra hecha!": "Purchase complete!", "Haz clic aquí": "Click here",
    "Ponértelo": "Equip it", "Quitártelo": "Remove it",

    // Perfil
    "Cambiar foto de perfil": "Change profile photo", "Editar perfil": "Edit profile", "Ajusta tu foto": "Adjust your photo",
    "Arrastra para moverla y usa el control para acercar.": "Drag to move it and use the slider to zoom.", "Vista previa de la foto": "Photo preview",
    "Acercar": "Zoom", "Guardar foto": "Save photo", "Quitar foto": "Remove photo", "(3 a 20 letras, números o _)": "(3 to 20 letters, numbers or _)",
    "5 minutos": "5 minutes", "10 minutos": "10 minutes", "15 minutos": "15 minutes", "30 minutos": "30 minutes",
    "¿Qué te describe mejor?": "What describes you best?", "Quiero cambiar de rumbo": "I want to change careers", "Guardar cambios": "Save changes",
    "Lo que llevas puesto": "What you're wearing", "En CódigoCamp desde el": "On CódigoCamp since", "Racha actual": "Current streak", "Mejor racha": "Best streak",
    "XP total": "Total XP", "Niveles superados": "Levels passed", "Lecciones hechas": "Lessons done", "Racha de": "Streak of",
    "Aún no tienes cosméticos. Gana diamantes en": "You don't have cosmetics yet. Earn diamonds in", "y consigue los tuyos en la": "and get yours in the",
    "Todavía no has terminado ninguna lección en": "You haven't finished any lesson in", "La imagen pesa más de 20 MB.": "The image is larger than 20 MB.",
    "No se pudo leer esa imagen.": "Couldn't read that image.", "Foto quitada": "Photo removed", "No se pudo quitar la foto.": "Couldn't remove the photo.",
    "No se pudo subir la foto.": "Couldn't upload the photo.", "¡Foto actualizada!": "Photo updated!", "Perfil actualizado": "Profile updated",
    "tienda": "shop", "recompensas": "rewards",

    // Chats
    "Amigos": "Friends", "Tu ID": "Your ID", "Copiar tu ID": "Copy your ID", "Copiar enlace de invitación": "Copy invite link", "Invitar": "Invite",
    "Busca por nombre, @usuario o ID": "Search by name, @username or ID", "Buscar personas por nombre, usuario o ID": "Search people by name, username or ID",
    "Conversación": "Conversation", "Tus conversaciones": "Your conversations",
    "Elige un amigo para chatear o agrega a alguien con su @usuario o ID.": "Pick a friend to chat with or add someone by @username or ID.",
    "Volver a la lista": "Back to the list", "Quitar amigo": "Remove friend", "Emojis rápidos": "Quick emojis", "Archivos para enviar": "Files to send",
    "Adjuntar fotos, videos o archivos (hasta 1 GB)": "Attach photos, videos or files (up to 1 GB)", "Mensaje": "Message", "Emojis": "Emojis",
    "Solicitudes enviadas": "Sent requests", "Solicitudes": "Requests",
    "Todavía no tienes amigos. Búscalos arriba por nombre o usuario, o mándales tu enlace de invitación.": "You don't have friends yet. Search for them above by name or username, or send them your invite link.",
    "📋 Copiar": "📋 Copy", "Nadie coincide. Prueba con su ID o su @usuario exacto.": "No matches. Try their ID or exact @username.",
    "Eliminar para todos": "Delete for everyone", "¿Eliminar este mensaje para todos?": "Delete this message for everyone?", "Hoy": "Today", "Ayer": "Yesterday",
    "Aceptar solicitud": "Accept request", "Rechazar": "Decline", "Enlace copiado": "Link copied",
    "📇 Buscar en mis contactos": "📇 Search my contacts", "Buscar en mis contactos": "Search my contacts",
    "Elige contactos de tu teléfono para ver quién ya está en CódigoCamp o invitarlos. No guardamos tu agenda.": "Pick contacts from your phone to see who's already on CódigoCamp or invite them. We don't store your address book.",
    "Ya está en CódigoCamp": "Already on CódigoCamp", "Invitar por mensaje": "Invite by message", "Agregar amigo": "Add friend",
    "Ninguno de esos contactos está en CódigoCamp todavía. ¡Invítalos!": "None of those contacts are on CódigoCamp yet. Invite them!",
    "Tu navegador no permite elegir contactos. Copia tu enlace de invitación y compártelo.": "Your browser doesn't support picking contacts. Copy your invite link and share it.",

    "Tus contactos": "Your contacts", "✓ Amigos": "✓ Friends", "Solicitud enviada": "Request sent", "✓ Listo": "✓ Done", "Guardado": "Saved",
    "Que mis contactos me encuentren": "Let my contacts find me",
    "Si alguien tiene tu correo en su teléfono y busca en sus contactos desde Chats, te verá para agregarte. Nadie ve tu correo.": "If someone has your email in their phone and searches their contacts from Chats, they'll see you and can add you. Nobody sees your email.",
    "Sin permiso para ver tus contactos. Puedes darlo en Ajustes del teléfono → Apps → CódigoCamp → Permisos.": "No permission to see your contacts. You can grant it in Phone settings → Apps → CódigoCamp → Permissions.",
    "El teléfono no respondió. Inténtalo otra vez.": "The phone didn't respond. Try again.", "📋 Copiar enlace de invitación": "📋 Copy invite link",
    "Enlace copiado: mándalo a quien quieras invitar": "Link copied: send it to whoever you want to invite", "Invitar por WhatsApp": "Invite via WhatsApp",
    "Invitar por mensaje": "Invite by text message", "Invitar por correo": "Invite by email",

    // Recompensas
    "CENTRO DE OPERACIONES": "OPERATIONS CENTER", "TEMPORADA ACTUAL": "CURRENT SEASON", "Tu tablero de misiones": "Your mission board",
    "Cumple encargos y logros, abre sus cofres y no pierdas tu racha.": "Complete quests and achievements, open their chests and keep your streak.",
    "Abriendo cofre": "Opening chest", "cofres por abrir": "chests to open", "encargos de hoy": "today's quests", "cofres de logro": "achievement chests",
    "puntos de temporada": "season points", "Secciones de recompensas": "Rewards sections", "📋 Encargos de hoy": "📋 Today's quests",
    "🎁 Cofres de logro": "🎁 Achievement chests", "🏆 Temporada": "🏆 Season", "Encargos de hoy": "Today's quests",
    "Cada encargo trae un cofre: se abre solo dentro de la lección en cuanto lo cumples.": "Each quest comes with a chest: it opens by itself in the lesson as soon as you complete it.",
    "LOGROS": "ACHIEVEMENTS", "Cofres de logro": "Achievement chests",
    "Primero los que puedes abrir, luego los que tienes más cerca. Dan diamantes, salvarrachas y cosméticos exclusivos.": "First the ones you can open, then the closest ones. They give diamonds, streak freezes and exclusive cosmetics.",
    "Desafío del mes": "Challenge of the month", "OBJETIVO": "GOAL", "DE TEMPORADA": "OF THE SEASON", "MISIÓN LARGA": "LONG MISSION",
    "Encadena tus misiones diarias para desbloquear la recompensa especial.": "Chain your daily missions to unlock the special reward.",
    "Acumula 60 puntos de misión": "Collect 60 mission points", "Progreso de temporada": "Season progress",
    "Cada encargo cumplido suma 5 puntos. ¿Quieres ver tus días de práctica? Míralos en el": "Each completed quest adds 5 points. Want to see your practice days? Check them in the",
    "calendario de racha de tu perfil": "streak calendar on your profile", ". Gasta tus diamantes en la": ". Spend your diamonds in the",
    "¡Desafío superado! Recibiste": "Challenge complete! You got", "Cofre de madera": "Wooden chest", "Cofre de plata": "Silver chest",
    "Cofre de oro": "Gold chest", "Cofre de diamante": "Diamond chest", "Cofre legendario": "Legendary chest", "¡Abrir cofre!": "Open chest!",
    "Toca el cofre para abrirlo": "Tap the chest to open it", "¡Conseguiste!": "You got!", "¡Puesto!": "Equipped!", "¡Encargo cumplido!": "Quest complete!",
    "Abrir": "Open", "Abierto": "Opened", "Bloqueado": "Locked", "Completado": "Completed", "Premio": "Prize", "Premio:": "Prize:",

    // Reto
    "Salir de la lección": "Exit the lesson", "Progreso de la lección": "Lesson progress", "Comprobar": "Check", "¿Seguro que quieres salir?": "Are you sure you want to leave?",
    "Si sales ahora perderás el avance de esta lección.": "If you leave now you'll lose this lesson's progress.", "Seguir aprendiendo": "Keep learning",
    "¡Te quedaste sin vidas!": "You're out of lives!",
    "Recupera una vida cada 30 minutos, gana recompensas practicando o compra vidas con diamantes.": "You get a life back every 30 minutes, earn rewards by practicing or buy lives with diamonds.",
    "Elige la respuesta correcta": "Choose the correct answer", "Encuentra el error": "Find the mistake", "Ordena los pasos": "Put the steps in order",
    "Escribe código": "Write code", "Caza el bug · pruebas de software": "Bug hunt · software testing", "Escribe tu respuesta": "Type your answer",
    "Toca las piezas en el orden correcto": "Tap the pieces in the right order", "Ejemplos (hay además pruebas ocultas)": "Examples (there are also hidden tests)",
    "No pude ejecutar tu código": "I couldn't run your code", "Prueba oculta superada": "Hidden test passed",
    "Prueba oculta fallida: piensa en los casos límite": "Hidden test failed: think about edge cases", "¡Todas las pruebas superadas!": "All tests passed!",
    "Pruebas superadas": "Tests passed", "Escribe los argumentos de entrada separados por comas. Los textos van entre comillas.": "Type the input arguments separated by commas. Strings go in quotes.",
    "No pude ejecutar la prueba": "I couldn't run the test", "¡Bug encontrado!": "Bug found!", "Con esa entrada ambas versiones dan lo mismo": "With that input both versions give the same result",
    "✅ ¡Muy bien!": "✅ Great job!", "❌ Todavía no": "❌ Not yet", "Probando…": "Testing…", "¡Nivel completado!": "Level complete!",
    "¡Hiciste la racha de hoy!": "You hit today's streak!", "¡Empezaste una racha nueva!": "You started a new streak!", "Continuar ➜": "Continue ➜",
    "Tiempo agotado: ¿tu código tiene un bucle infinito?": "Time's up: does your code have an infinite loop?", "Error al ejecutar el código": "Error running the code",
    "No se pudo ejecutar": "Couldn't run", "Siguiente": "Next", "Saltar": "Skip", "Pista": "Hint", "Correcto": "Correct", "Incorrecto": "Incorrect",

    // Aprende
    "Ruta de aprendizaje": "Learning path", "Elige un lenguaje": "Choose a language", "Ocultar este panel": "Hide this panel", "◀ Ocultar": "◀ Hide",
    "Buscar lección…": "Search lesson…", "Buscar lección": "Search lesson", "Progreso del curso": "Course progress", "¿Otro lenguaje?": "Another language?",
    "Pregúntale al tutor": "Ask the tutor", "Mostrar lenguajes y lecciones": "Show languages and lessons", "▶ Lenguajes y lecciones": "▶ Languages and lessons",
    "Práctica": "Practice", "Pruébalo tú": "Try it yourself", "Restablecer": "Reset", "▶ Ejecutar": "▶ Run", "Editor de código": "Code editor",
    "Resultado": "Output", "← Anterior": "← Previous", "Marcar como hecha y seguir": "Mark as done and continue", "Marcar como hecha y terminar": "Mark as done and finish",
    "Pulsa «Ejecutar» (o Ctrl + Enter) para ver el resultado.": "Press “Run” (or Ctrl + Enter) to see the result.",
    "No se pudo cargar el catálogo de cursos. Se mostrarán los cursos disponibles en esta versión.": "Couldn't load the course catalog. The courses included in this version will be shown.",
    "Ninguna lección coincide.": "No lesson matches.", "lecciones hechas": "lessons done", "lección": "lesson", "¿Qué es?": "What is it?",
    "¿Para qué sirve?": "What is it for?", "Puntos clave": "Key points", "Mira el código": "Look at the code",
    "Los comentarios del código te explican cada parte.": "The code comments explain each part.", "⚠️ Error común": "⚠️ Common mistake", "🎯 Ahora tú": "🎯 Your turn",
    "Muestra el resultado esperado": "Shows the expected output", "Se ve al instante": "Shows instantly", "Ejemplos para copiar": "Examples to copy",
    "Se ve al instante (React 19)": "Shows instantly (React 19)", "Se ejecuta en tu navegador": "Runs in your browser",
    "No se pudo descargar el motor. Revisa tu conexión.": "Couldn't download the engine. Check your connection.",
    "Tiempo agotado: ¿hay un bucle infinito?": "Time's up: is there an infinite loop?", "Consulta ejecutada. No devolvió filas.": "Query executed. It returned no rows.",
    "Ejecutando…": "Running…", "(el programa no mostró nada)": "(the program printed nothing)",

    // IA
    "Tutor de IA": "AI tutor", "Cerrar la lista": "Close the list", "Buscar en tus chats": "Search your chats", "Buscar conversaciones": "Search conversations",
    "Conversaciones guardadas": "Saved conversations", "Conversación con el tutor": "Conversation with the tutor", "Conversación nueva": "New conversation",
    "Nueva conversación": "New conversation", "Opciones de la conversación": "Conversation options", "¿En qué te ayudo hoy?": "How can I help you today?",
    "Pregunta lo que quieras, pega tu código o adjunta archivos.": "Ask anything, paste your code or attach files.", "Escribe tu pregunta…": "Type your question…",
    "Tu pregunta": "Your question", "Adjuntar imágenes, capturas, PDF, video, audio o código (hasta 1 GB)": "Attach images, screenshots, PDFs, video, audio or code (up to 1 GB)",
    "Insertar un bloque de código": "Insert a code block", "Respuesta copiada": "Answer copied",
    "Pregunta lo que quieras, pega tu código o adjunta una captura.": "Ask anything, paste your code or attach a screenshot.",
    "Últimos 7 días": "Last 7 days", "Últimos 30 días": "Last 30 days", "Anteriores": "Older", "Fijadas": "Pinned",
    "Nuevo nombre de la conversación": "New conversation name", "Conversación fijada": "Conversation pinned", "Conversación desfijada": "Conversation unpinned",
    "Conversación anterior": "Previous conversation", "Explícame qué es una variable": "Explain what a variable is", "Revisa mi código": "Review my code",
    "Dame un ejercicio fácil": "Give me an easy exercise", "¿Qué error es este y cómo lo arreglo?": "What's this error and how do I fix it?",
    "Explícame esta captura de pantalla": "Explain this screenshot", "¿Cómo conecto mi app con MySQL de XAMPP?": "How do I connect my app to XAMPP's MySQL?",
    "Escribe tu pregunta… (Enter envía · Shift + Enter, salto de línea)": "Type your question… (Enter sends · Shift + Enter, new line)",
    "Revisando tus archivos…": "Checking your files…", "Pensando…": "Thinking…", "Copiar respuesta": "Copy answer",

    // Trabajo
    "Secciones de Trabajo": "Workspace sections", "Archivos": "Files", "Código": "Code", "Terminal": "Terminal", "Archivos del proyecto": "Project files",
    "Nuevo archivo": "New file", "Nueva carpeta": "New folder", "Contraer carpetas": "Collapse folders", "Ir a un archivo (Ctrl+P)": "Go to file (Ctrl+P)",
    "Ir a un archivo": "Go to file", "Subir, importar .zip, descargar o abrir carpeta del computador": "Upload, import .zip, download or open a computer folder",
    "Más acciones: subir, importar, descargar o abrir carpeta": "More actions: upload, import, download or open folder", "Vistas de la barra lateral": "Sidebar views",
    "Archivos (Ctrl+Shift+E)": "Explorer (Ctrl+Shift+E)", "Control de código fuente (Ctrl+Shift+G)": "Source control (Ctrl+Shift+G)", "Control de código fuente": "Source control",
    "Extensiones: librerías y frameworks (Ctrl+Shift+X)": "Extensions: libraries and frameworks (Ctrl+Shift+X)", "Extensiones: librerías y frameworks": "Extensions: libraries and frameworks",
    "Extensiones": "Extensions", "Buscar en archivos (Ctrl+Shift+F)": "Search in files (Ctrl+Shift+F)", "Buscar en archivos": "Search in files",
    "Mi proyecto": "My project", "Guardado en tu cuenta": "Saved to your account", "NUBE": "CLOUD", "Cambiar el ancho de la lista de archivos": "Resize the file list",
    "Editor": "Editor", "Archivos abiertos": "Open files", "Abrir vista previa de la página": "Open page preview", "Abrir vista previa": "Open preview",
    "Guardar ahora (Ctrl+S)": "Save now (Ctrl+S)", "Guardar ahora": "Save now", "Ejecutar el archivo abierto (Ctrl+Enter)": "Run the open file (Ctrl+Enter)",
    "Ejecutar archivo": "Run file", "Ejecutar": "Run", "Ruta del archivo": "File path", "Bienvenida": "Welcome", "¡Manos a la obra!": "Let's get to work!",
    "Abrir la terminal": "Open the terminal", "Subir archivos": "Upload files", "Importar .zip": "Import .zip", "Abrir carpeta del computador": "Open computer folder",
    "Con un archivo abierto,": "With a file open,", "lo ejecuta.": "runs it.", "Cambiar el ancho de la vista previa": "Resize the preview",
    "Vista previa del proyecto": "Project preview", "Vistas previas abiertas": "Open previews", "Página anterior": "Previous page", "Página siguiente": "Next page",
    "Recargar la vista previa": "Reload the preview", "Ver otra página de tu proyecto": "View another page of your project", "Página que se muestra": "Page shown",
    "Vista previa": "Preview", "Dirección del servidor": "Server address",
    "En vivo: la vista se recarga sola cuando cambias tus archivos (como Live Server)": "Live: the view reloads by itself when you change your files (like Live Server)",
    "En vivo": "Live", "Tamaño: ajustar al panel": "Size: fit to panel", "Cambiar el tamaño de la pantalla": "Change the screen size", "Ver al lado del código": "View next to the code",
    "Abrir en otra pestaña del navegador (se actualiza en vivo)": "Open in another browser tab (updates live)", "Abrir en otra pestaña": "Open in another tab",
    "Cerrar la vista previa": "Close the preview", "Abrir en el navegador": "Open in the browser", "Abre tu página en cualquier navegador": "Open your page in any browser",
    "Como Live Server: los enlaces entre tus páginas funcionan y se recarga sola cuando guardas. Sirve en tu celular o para mostrársela a alguien.": "Like Live Server: links between your pages work and it reloads by itself when you save. It works on your phone or to show it to someone.",
    "Dirección de tu página": "Your page's address", "El enlace anterior deja de funcionar": "The previous link stops working", "Cambiar enlace": "Change link",
    "⚠️ Entraste a CódigoCamp por": "⚠️ You opened CódigoCamp through", "del archivo": "of the file", "Cambiar la altura de la terminal": "Resize the terminal",
    "Terminal y consola": "Terminal and console", "Asistente de programación": "Coding assistant", "Asistente": "Assistant", "Tutor de CódigoCamp": "CódigoCamp tutor",
    "Con esto activo la IA ve tu proyecto y puede proponer cambios en tus archivos. Nada se aplica sin que lo aceptes.": "With this on, the AI sees your project and can suggest changes to your files. Nothing is applied unless you accept it.",
    "Editar con IA": "Edit with AI", "(Gemini): la IA puede proponer cambios en tus archivos; tú los aceptas": "(Gemini): the AI can suggest changes to your files; you accept them",
    "Archivos para la IA": "Files for the AI", "Pregunta sobre tu código, pide un cambio («agrega un botón de modo oscuro»)… Enter envía": "Ask about your code, request a change (“add a dark mode button”)… Enter sends",
    "Pregunta para el asistente": "Question for the assistant", "Adjuntar capturas, PDF, video, audio o archivos (hasta 1 GB)": "Attach screenshots, PDFs, video, audio or files (up to 1 GB)",
    "Adjuntar archivos": "Attach files", "Preguntar": "Ask", "Usa Gemini con la clave de CódigoCamp (GEMINI_API_KEY).": "Uses Gemini with CódigoCamp's key (GEMINI_API_KEY).",
    "Rama de Git (muestra el estado en la terminal)": "Git branch (shows the status in the terminal)", "Estado del guardado (clic para guardar ahora)": "Save status (click to save now)",
    "Sincronizando…": "Syncing…", "Guardado": "Saved", "Sin guardar": "Unsaved", "Carpeta del computador vinculada": "Linked computer folder",
    "Servidor de Python encendido: clic para abrirlo en la vista previa": "Python server running: click to open it in the preview",
    "Activa o desactiva el guardado automático. Desactivado, guardas tú con Ctrl+S.": "Turns autosave on or off. When off, you save with Ctrl+S.",
    "Autoguardado: Sí": "Autosave: On", "✨ Copiloto: Sí": "✨ Copilot: On", "✨ Copiloto: No": "✨ Copilot: Off", "Copiloto desactivado": "Copilot turned off",
    "Copiloto activado: la IA sugiere en gris mientras escribes. Tab acepta.": "Copilot on: the AI suggests in gray as you type. Tab accepts.",
    "La IA sugiere el código que sigue mientras escribes (Tab acepta, Esc descarta)": "The AI suggests the next code as you type (Tab accepts, Esc dismisses)", "Autoguardado: No": "Autosave: Off", "Problemas": "Problems", "Espacios: 2": "Spaces: 2", "Texto sin formato": "Plain Text",
    "Mostrar u ocultar la terminal (Ctrl+`)": "Show or hide the terminal (Ctrl+`)", "Mostrar u ocultar el asistente": "Show or hide the assistant",
    "Aceptar cambios": "Accept changes", "Descartar": "Discard", "Aplicar": "Apply", "Cambios propuestos": "Proposed changes", "Nueva vista previa": "New preview",
    "Cuentas de GitHub": "GitHub accounts", "Agregar otra cuenta": "Add another account", "Cerrar sesión en GitHub": "Log out of GitHub", "Usar esta cuenta": "Use this account",
    "Cerrar todas las cuentas": "Log out of all accounts", "Iniciar sesión con GitHub": "Sign in with GitHub", "Mover a…": "Move to…", "Nombre nuevo": "New name",
    "Descargar": "Download", "Duplicar": "Duplicate", "Copiar ruta": "Copy path",

    // Acceso
    "← Volver al inicio": "← Back to home", "Te estábamos esperando": "We were waiting for you", "Bienvenido": "Welcome", "de vuelta": "back",
    "Entra a tu cuenta y sigue aprendiendo justo donde lo dejaste.": "Sign in and keep learning right where you left off.",
    "Lecciones de más de 16 lenguajes": "Lessons in more than 16 languages", "Laboratorio en vivo, sin instalar nada": "Live lab, nothing to install",
    "Tutor de IA que responde en español": "AI tutor that answers in Spanish", "Iniciar sesión": "Sign in", "Usa el correo con el que te registraste.": "Use the email you signed up with.",
    "Correo": "Email", "Contraseña": "Password", "Tu contraseña": "Your password", "¿Olvidaste tu contraseña?": "Forgot your password?", "Entrar": "Sign in",
    "Iniciar sesión con Google": "Sign in with Google", "¿No tienes cuenta?": "Don't have an account?", "Regístrate gratis": "Sign up for free",
    "Escribe el correo de tu cuenta y te enviaremos un enlace para crear una nueva. Sirve una sola vez y vence en 30 minutos.": "Enter your account email and we'll send you a link to create a new one. It works once and expires in 30 minutes.",
    "Enviarme el enlace": "Send me the link", "← Volver a iniciar sesión": "← Back to sign in", "Recordarme": "Remember me", "Mostrar contraseña": "Show password",
    "Ocultar contraseña": "Hide password", "Esperando a Google…": "Waiting for Google…",
    "Termina de entrar con Google en el navegador que se abrió. Cuando termines, vuelve a la app: se conecta sola.": "Finish signing in with Google in the browser that opened. When you're done, come back to the app: it connects by itself.",
    "Gratis · En español · A tu ritmo": "Free · In Spanish · At your pace", "Crea tu cuenta y": "Create your account and", "empieza a programar": "start coding",
    "Es gratis y en menos de un minuto estás dentro. Sin instalar nada.": "It's free and you're in in under a minute. Nothing to install.",
    "Laboratorio en vivo de HTML, CSS y JavaScript": "Live lab for HTML, CSS and JavaScript", "Tutor de IA que responde tus dudas en español": "AI tutor that answers your questions in Spanish",
    "Crear cuenta": "Create account", "Solo necesitas un nombre, un correo y una contraseña, o tu cuenta de Google.": "You only need a name, an email and a password, or your Google account.",
    "Cómo quieres que te llamemos": "What should we call you", "(mínimo 6 caracteres)": "(at least 6 characters)",
    "Mínimo 6 caracteres, con una mayúscula y un número": "At least 6 characters, with an uppercase letter and a number", "Crea una contraseña": "Create a password",
    "Mínimo 6 caracteres": "At least 6 characters", "Una letra mayúscula": "An uppercase letter", "Un número": "A number", "Escríbela otra vez": "Type it again",
    "Al crear tu cuenta, en el siguiente paso leerás y aceptarás los": "When you create your account, in the next step you'll read and accept the",
    "Registrarse con Google": "Sign up with Google", "¿Ya tienes cuenta?": "Already have an account?", "Inicia sesión": "Sign in",
    "Crea una nueva contraseña": "Create a new password", "Comprobando el enlace…": "Checking the link…", "mínimo 6 caracteres, una mayúscula y un número": "at least 6 characters, an uppercase letter and a number",
    "Tu nueva contraseña": "Your new password", "Repite la contraseña": "Repeat the password", "Otra vez, para confirmar": "Again, to confirm",
    "Guardar contraseña": "Save password", "Pedir un enlace nuevo": "Request a new link", "← Iniciar sesión": "← Sign in",

    // Portada
    "Aprende a programar": "Learn to code", "desde cero": "from scratch", "con un tutor de IA": "with an AI tutor",
    "Lecciones breves de más de 16 lenguajes, un laboratorio donde ves el resultado al instante y un tutor que responde tus dudas cuando te atascas.": "Short lessons in more than 16 languages, a lab where you see the result instantly and a tutor that answers your questions when you get stuck.",
    "Empezar a aprender": "Start learning", "Ya tengo cuenta": "I already have an account", "Qué vas a aprender": "What you'll learn",
    "✓ Resultado al instante, sin instalar nada": "✓ Instant results, nothing to install", "«Te explico el código línea por línea»": "“I'll explain the code line by line”",
    "Laboratorio en vivo": "Live lab", "HTML, CSS y JavaScript": "HTML, CSS and JavaScript", "© 2026 CódigoCamp · Aprende a programar en español": "© 2026 CódigoCamp · Learn to code in Spanish",

    // Onboarding
    "CódigoCamp, volver al inicio": "CódigoCamp, back to home", "Volver a la pregunta anterior": "Back to the previous question", "Progreso de las preguntas": "Question progress",
    "¿Cuál describe mejor tu punto de partida?": "Which best describes your starting point?", "¿Quién eres?": "Who are you?", "Soy estudiante": "I'm a student",
    "Trabajo y quiero cambiar de rumbo": "I work and want to change careers", "Ya programo y quiero mejorar": "I already code and want to improve",
    "Solo tengo curiosidad": "I'm just curious", "¿Qué proyectos quieres crear?": "What projects do you want to build?", "¿Qué te gustaría crear?": "What would you like to build?",
    "Páginas web": "Websites", "Apps para el móvil": "Mobile apps", "Videojuegos": "Video games", "Datos e inteligencia artificial": "Data and artificial intelligence",
    "Automatizar tareas": "Automate tasks", "Bases de datos": "Databases", "¿Qué experiencia tienes programando?": "How much coding experience do you have?",
    "Tu nivel": "Your level", "Empiezo desde cero": "Starting from zero", "Nunca he escrito código": "I've never written code", "He probado algo": "I've tried a bit",
    "Sé qué es una variable": "I know what a variable is", "Sé lo básico": "I know the basics", "Hago programas sencillos": "I write simple programs",
    "Tengo experiencia": "I have experience", "Quiero aprender algo nuevo": "I want to learn something new", "Selecciona un lenguaje para iniciar.": "Pick a language to start.",
    "Elige tu primer curso": "Choose your first course", "Recomendado": "Recommended", "La estructura de las páginas web": "The structure of web pages",
    "Estilos y diseño de páginas": "Page styling and design", "SQL, MongoDB, Redis y más": "SQL, MongoDB, Redis and more", "El lenguaje de la web": "The language of the web",
    "Datos, IA y automatización": "Data, AI and automation", "JavaScript con tipos": "JavaScript with types", "Apps y sistemas grandes": "Apps and large systems",
    "Videojuegos con Unity": "Video games with Unity", "Apps para Android": "Android apps", "Apps para iPhone": "iPhone apps", "Páginas con servidor": "Server-side pages",
    "Código fácil de leer": "Easy-to-read code", "Servidores rápidos": "Fast servers", "Rápido y seguro": "Fast and safe", "Cerca de la máquina": "Close to the machine",
    "Rendimiento y videojuegos": "Performance and video games", "Terminales": "Terminals", "Bash, PowerShell y CMD": "Bash, PowerShell and CMD", "Git y GitHub": "Git and GitHub",
    "Versiones y trabajo en equipo": "Versioning and teamwork", "Contenedores para tus apps": "Containers for your apps", "JavaScript en el servidor": "JavaScript on the server",
    "Equipo, Actions y Pages": "Teams, Actions and Pages", "MongoDB, Redis y más": "MongoDB, Redis and more", "Interfaces con componentes y hooks": "Interfaces with components and hooks",
    "Define tu ritmo de práctica.": "Set your practice pace.", "5 minutos al día": "5 minutes a day", "Tranquilo": "Easy", "10 minutos al día": "10 minutes a day",
    "Constante": "Steady", "15 minutos al día": "15 minutes a day", "Intenso": "Intense", "30 minutos al día": "30 minutes a day", "Máximo": "Maximum",
    "Antes de empezar, lee esto.": "Before you start, read this.", "Tu progreso está a salvo": "Your progress is safe",
    "(XP, racha y diamantes quedan en la base de datos), pero": "(XP, streak and diamonds stay in the database), but", "tus proyectos de Trabajo no": "your Workspace projects aren't",
    ": se pueden perder con las actualizaciones de CódigoCamp. Descárgalos en .zip o súbelos a GitHub.": ": they can be lost with CódigoCamp updates. Download them as .zip or push them to GitHub.",
    "Cargando los términos…": "Loading the terms…", "Aceptar los términos": "Accept the terms", "Entiendo que debo guardar copia de mis proyectos": "I understand I must back up my projects",
    "Trabajo no está en la base de datos: lo descargaré en .zip o lo subiré a GitHub": "Workspace isn't in the database: I'll download it as .zip or push it to GitHub",
    "Entiendo que la IA puede equivocarse": "I understand the AI can make mistakes", "Y no compartiré contraseñas ni datos sensibles": "And I won't share passwords or sensitive data",
    "Leí y acepto los Términos y condiciones": "I have read and accept the Terms and conditions", "Incluye las reglas de respeto en chats": "Includes the rules for respectful chats",
    "También puedes leerlos en una página aparte:": "You can also read them on a separate page:", "Tu ruta de aprendizaje está lista.": "Your learning path is ready.",
    "Tu primer curso": "Your first course", "Tu meta diaria": "Your daily goal", "Comienza con retos breves, gana experiencia y desbloquea nuevas etapas.": "Start with short challenges, earn experience and unlock new stages.",
    "Tu perfil mientras respondes": "Your profile as you answer", "Punto de partida": "Starting point", "Lo que quieres crear": "What you want to build",
    "Experiencia": "Experience", "Primer lenguaje": "First language", "Ritmo": "Pace", "Términos": "Terms", "Tu ruta": "Your path", "Tip: usa las teclas": "Tip: use the",
    "para elegir y": "keys to choose and", "para seguir.": "to continue.",

    // Misiones y logros (vienen del servidor)
    "Termina un nivel sin fallos": "Finish a level with no mistakes", "Escríbele a un amigo en Chats": "Message a friend in Chats",
    "Pregúntale algo al tutor de IA": "Ask the AI tutor something", "Ejecuta tu código en Trabajo": "Run your code in Workspace",
    "Haz 1 lección en Aprende y 1 nivel de retos": "Do 1 lesson in Learn and 1 challenge level", "Completa tu primera lección": "Complete your first lesson",
    "Agrega a un amigo en Chats": "Add a friend in Chats", "Primer paso": "First step", "Retador": "Challenger", "Una semana": "One week",
    "Un mes": "One month", "Leyenda": "Legend", "Estudiante": "Student", "Aprendiz": "Apprentice", "Social": "Social", "Imparable": "Unstoppable",
    "Maratón de retos": "Challenge marathon", "Encargado": "Quest master", "Dos meses": "Two months", "Sabio": "Sage", "Mito": "Myth", "Cien días": "One hundred days",
    "Empieza tu racha hoy": "Start your streak today", "Tu perfil": "Your profile", "Diamantes: se ganan en Recompensas y se gastan en la tienda": "Diamonds: earn them in Rewards and spend them in the shop",
    "Racha de días": "Day streak", "días de racha": "day streak", "días este mes": "days this month", "sin práctica": "no practice", "con práctica": "practiced",
    "Días practicados": "Days practiced", "Salvarrachas usado": "Streak freeze used",
    "Salvarrachas: si un día no practicas, se gasta uno solo y tu racha no se pierde. Tienes 0 de 2. Se consiguen en la tienda y en los cofres.": "Streak freezes: if you skip a day, one is used automatically and your streak is kept. You have 0 of 2. Get them in the shop and from chests.",
    "Salvarrachas: si un día no practicas, se gasta uno solo y tu racha no se pierde. Tienes 1 de 2. Se consiguen en la tienda y en los cofres.": "Streak freezes: if you skip a day, one is used automatically and your streak is kept. You have 1 of 2. Get them in the shop and from chests.",
    "Salvarrachas: si un día no practicas, se gasta uno solo y tu racha no se pierde. Tienes 2 de 2. Se consiguen en la tienda y en los cofres.": "Streak freezes: if you skip a day, one is used automatically and your streak is kept. You have 2 of 2. Get them in the shop and from chests.",
    "Aún no tienes conversaciones. Escribe tu primera pregunta.": "No conversations yet. Ask your first question.",
    "En vivo: la vista se recarga sola cuando cambias tus archivos (clic para pausar)": "Live: the view reloads by itself when you change your files (click to pause)",
    "Consola de la vista previa": "Preview console", "Guardado en tu cuenta (clic para guardar ahora)": "Saved to your account (click to save now)", "Sin problemas": "No problems",
    "ENCARGO ACTIVO": "ACTIVE QUEST", "COMPLETADO": "COMPLETED", "COFRE": "CHEST", "COFRE ABIERTO": "CHEST OPENED", "DÍA": "DAY", "DÍAS": "DAYS",

    // Widget
    "Vista del widget": "Widget view", "🔥 Racha": "🔥 Streak", "🎯 Meta": "🎯 Goal", "📅 Semana": "📅 Week", "Widget flotante (siempre encima)": "Floating widget (always on top)",
    "Widget flotante": "Floating widget", "📋 Hoy": "📋 Today", "⚡ Reto": "⚡ Quiz",
    "¡Bien hecho! Tu racha está a salvo 💪": "Well done! Your streak is safe 💪", "¡Hoy cumpliste! Nos vemos mañana": "Done for today! See you tomorrow",
    "¡Qué crack! Ya practicaste hoy": "Legend! You already practiced today", "¡Estás en llamas! 🔥": "You're on fire! 🔥", "¡Racha imparable! Sigue así": "Unstoppable streak! Keep it up",
    "Nadie te para 🚀": "Nobody can stop you 🚀", "¿Practicamos un ratito hoy?": "Shall we practice a bit today?", "Tu racha te está esperando 👀": "Your streak is waiting for you 👀",
    "5 minutos y listo, ¿vamos?": "Just 5 minutes, shall we?", "¡Tu racha está en peligro! 😱": "Your streak is in danger! 😱", "¡Corre! Se acaba el día": "Hurry! The day is ending",
    "¡No dejes que se apague tu racha!": "Don't let your streak go out!", "Zzz… despiértame con una lección": "Zzz… wake me up with a lesson", "Empieza una racha hoy ✨": "Start a streak today ✨",
    "¿Hoy empezamos? Yo te acompaño": "Shall we start today? I'll be with you", "✅ ¡Correcto!": "✅ Correct!", "❌ Casi": "❌ Almost",
    "Reto rápido de repaso · cambia cada 30 min": "Quick review quiz · changes every 30 min", "Elige un curso en CódigoCamp para tener retos rápidos aquí.": "Choose a course on CódigoCamp to get quick quizzes here.",
    "día de racha": "day streak", "días de racha": "day streak", "Mejor racha:": "Best streak:", "¡Ya practicaste hoy! 💪": "You already practiced today! 💪",
    "Practica hoy para no perder tu racha": "Practice today so you don't lose your streak", "Sin conexión": "Offline",
  };

  var MES = { enero: "January", febrero: "February", marzo: "March", abril: "April", mayo: "May", junio: "June", julio: "July", agosto: "August", septiembre: "September", octubre: "October", noviembre: "November", diciembre: "December" };
  var PATRONES = [
    [/^(\d+) días? de racha$/, "$1-day streak"],
    [/^(\d+)\/100 XP para el siguiente nivel$/, "$1/100 XP to the next level"],
    [/^Nivel (\d+)$/, "Level $1"], [/^ETAPA (\d+) DE (\d+)$/, "STAGE $1 OF $2"], [/^ETAPA (\d+)$/, "STAGE $1"], [/^SECCIÓN (\d+)$/, "SECTION $1"],
    [/^(\d+)% completado$/, "$1% complete"], [/^Curso de (.+)$/, "$1 course"], [/^Lecciones de (.+)$/, "$1 lessons"], [/^Tu avance en (.+)$/, "Your progress in $1"],
    [/^(\d+) lecciones hechas$/, "$1 lessons done"], [/^(\d+)\/(\d+) lecciones hechas$/, "$1/$2 lessons done"], [/^Practicar (.+) con retos →$/, "Practice $1 with challenges →"],
    [/^Los retos de (.+) llegan pronto$/, "$1 challenges are coming soon"], [/^¡Terminaste todas las lecciones de (.+)! 🎉$/, "You finished all the $1 lessons! 🎉"],
    [/^No se pudieron cargar las lecciones de (.+)\.?$/, "Couldn't load the $1 lessons."], [/^Soy tu tutor de (.+)\. Pregunta, pega tu código o adjunta una captura\.$/, "I'm your $1 tutor. Ask, paste your code or attach a screenshot."],
    [/^Explícame lo más importante de (.+)$/, "Explain the most important things about $1"], [/^¿Borrar «(.+)»\? No se puede deshacer\.$/, "Delete “$1”? This can't be undone."],
    [/^Racha de (\d+) días?$/, "$1-day streak"], [/^(\d+) días?$/, function (m, n) { return n + " day" + (n === "1" ? "" : "s"); }],
    [/^(\d+) ?H RESTANTES$/, "$1H LEFT"], [/^(\d+) DÍAS?$/, "$1 DAYS"], [/^Desafío de (.+)$/, "$1 challenge"], [/^te faltan (\d+)$/, "you need $1 more"],
    [/^❌ Casi\. Respuesta correcta: (.+)$/, "❌ Almost. Correct answer: $1"], [/^(.+) · CódigoCamp$/, function (m, t) { return (tr(t) || t) + " · CódigoCamp"; }],
    [/^PASO (\d+) \/ (\d+)$/, "STEP $1 / $2"], [/^Actualizado (\d{1,2}:\d{2})$/, "Updated $1"], [/^Sin conexión · (.*)$/, "Offline · $1"], [/^(\d+)\/(\d+) encargos · Ver cofres →$/, "$1/$2 quests · See chests →"],
    [/^días · 🧊 (\d+) salvarrachas$/, "days · 🧊 $1 streak freezes"], [/^⚠️ Practica antes de medianoche o pierdes tu racha de (\d+)$/, "⚠️ Practice before midnight or you'll lose your $1-day streak"],
    [/^Ya está en CódigoCamp \((\d+)\)$/, "Already on CódigoCamp ($1)"], [/^Invitar \((\d+)\)$/, "Invite ($1)"],
    [/^¡Ahora eres amigo de (.+)!$/, "You're now friends with $1!"], [/^Solicitud enviada a (.+)$/, "Request sent to $1"], [/^Premio: (.+)$/, function (m, p) { return "Prize: " + (tr(p) || p); }],
    [/^Progreso: (.+)$/, function (m, p) { return "Progress: " + (tr(p) || p); }], [/^Acciones de (.+)$/, "Actions for $1"],
    [/^¿En qué te ayudo hoy, (.+)\?$/, "How can I help you today, $1?"], [/^ETAPA (\d+), SECCIÓN (\d+)$/, "STAGE $1, SECTION $2"],
    [/^parte (\d+) de (\d+)$/, "part $1 of $2"], [/^(\d+) de (\d+) lecciones hechas$/, "$1 of $2 lessons done"],
    [/^Gana (\d+) XP$/, "Earn $1 XP"], [/^Gana (\d+) XP y completa (\d+) niveles$/, "Earn $1 XP and complete $2 levels"],
    [/^Completa (\d+) (?:nivel|niveles)( de retos)?$/, function (m, n) { return "Complete " + n + " challenge level" + (n === "1" ? "" : "s"); }],
    [/^Termina (un|\d+) (?:nivel|niveles) sin fallos$/, function (m, n) { return n === "un" ? "Finish a level with no mistakes" : "Finish " + n + " levels with no mistakes"; }],
    [/^Completa (\d+) lecci(?:ón|ones) en Aprende$/, function (m, n) { return "Complete " + n + " lesson" + (n === "1" ? "" : "s") + " in Learn"; }],
    [/^Completa (\d+) lecciones$/, "Complete $1 lessons"], [/^Practica (\d+) días seguidos$/, "Practice $1 days in a row"],
    [/^Supera (\d+) niveles de retos$/, "Pass $1 challenge levels"], [/^Supera (\d+) encargos diarios$/, "Complete $1 daily quests"],
    [/^Ten (\d+) amigos en Chats$/, "Have $1 friends in Chats"], [/^Envía (\d+) mensajes en Chats$/, "Send $1 messages in Chats"],
    [/^Hazle (\d+) preguntas al tutor de IA$/, "Ask the AI tutor $1 questions"], [/^Ejecuta tu código (\d+) veces en Trabajo$/, "Run your code $1 times in Workspace"],
    [/^Maratón: completa (\d+) niveles$/, "Marathon: complete $1 levels"], [/^Exclusivo del cofre «(.+)»\.$/, function (m, c) { return "Exclusive to the “" + (tr(c) || c) + "” chest."; }],
    [/^Racha de (\d+) días$/, "$1-day streak"],
    [/^(\d{1,2}) de (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre) de (\d{4})$/i, function (m, d, mes, a) { return MES[mes.toLowerCase()] + " " + d + ", " + a; }],
    [/^(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre) de (\d{4})$/i, function (m, mes, a) { return MES[mes.toLowerCase()] + " " + a; }],
    [/^En CódigoCamp desde el (.+)$/, function (m, f) { return "On CódigoCamp since " + (tr(f) || f); }], [/^(\d+) diamantes?$/, "$1 diamonds"],
    [/^\+(\d+) diamantes?$/, "+$1 diamonds"], [/^(\d+) vidas?$/, "$1 lives"], [/^(\d+) salvarrachas$/, "$1 streak freezes"], [/^hace (\d+) min$/, "$1 min ago"],
    [/^hace (\d+) h$/, "$1 h ago"], [/^hace (\d+) días?$/, "$1 days ago"], [/^Cofre (\d+) de (\d+)$/, "Chest $1 of $2"], [/^(\d+) de (\d+)$/, "$1 of $2"],
  ];

  function tr(s) {
    if (!s || s.length > 400) return null;
    if (Object.prototype.hasOwnProperty.call(D, s)) return D[s];
    for (var i = 0; i < PATRONES.length; i++) {
      var p = PATRONES[i];
      if (p[0].test(s)) return s.replace(p[0], p[1]);
    }
    if (s.indexOf(" · ") > 0 && !/ · CódigoCamp$/.test(s)) {   // «Primer paso · Completa tu primera lección»: cada parte por separado
      var partes = s.split(" · "), cambio = false;
      for (var k = 0; k < partes.length; k++) { var r = tr(partes[k]); if (r != null) { partes[k] = r; cambio = true; } }
      if (cambio) return partes.join(" · ");
    }
    return null;
  }

  /** Traduce conservando los espacios de los lados (p. ej. " Guardar "). */
  function traducir(texto) {
    var t = texto.trim();
    if (!t || !/[a-záéíóúñ]/i.test(t)) return null;
    var r = tr(t);
    if (r == null) {
      var limpio = t.replace(/\s+/g, " ");
      if (limpio !== t) r = tr(limpio);
    }
    if (r == null) return null;
    var i = texto.indexOf(t);
    return texto.slice(0, i) + r + texto.slice(i + t.length);
  }
  window.ccT = function (s) { var r = s == null ? null : traducir(String(s)); return r == null ? s : r; };

  var SALTAR = "script,style,code,pre,textarea,svg,.monaco-editor,.xterm,[data-sin-traducir],.cm,.msg-cuerpo,#teoria,#ed,#out,.cm-menu .cm-prev";
  var ATRIBUTOS = ["placeholder", "title", "aria-label", "alt"];

  function saltar(el) { return !el || (el.closest && el.closest(SALTAR)); }

  function nodoTexto(n) {
    if (saltar(n.parentElement)) return;
    var r = traducir(n.data);
    if (r != null && r !== n.data) n.data = r;
  }
  function atributos(el) {
    if (el.closest && el.closest("[data-sin-traducir],.cm,.msg-cuerpo")) return;
    for (var i = 0; i < ATRIBUTOS.length; i++) {
      var a = ATRIBUTOS[i], v = el.getAttribute(a);
      if (v) { var r = traducir(v); if (r != null && r !== v) el.setAttribute(a, r); }
    }
    if (el.tagName === "INPUT" && /^(button|submit)$/i.test(el.type) && el.value) { var rv = traducir(el.value); if (rv != null) el.value = rv; }
  }
  function recorrer(raiz) {
    if (raiz.nodeType === 3) return nodoTexto(raiz);
    if (raiz.nodeType !== 1 || saltar(raiz)) return;
    atributos(raiz);
    var w = document.createTreeWalker(raiz, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) { return n.nodeType === 1 && saltar(n) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT; },
    });
    var n;
    while ((n = w.nextNode())) { if (n.nodeType === 3) nodoTexto(n); else atributos(n); }
  }

  var obs = new MutationObserver(function (lista) {
    for (var i = 0; i < lista.length; i++) {
      var m = lista[i];
      if (m.type === "characterData") nodoTexto(m.target);
      else if (m.type === "attributes") { if (!saltar(m.target)) atributos(m.target); }
      else for (var j = 0; j < m.addedNodes.length; j++) recorrer(m.addedNodes[j]);
    }
  });
  obs.observe(document.documentElement, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATRIBUTOS });
  document.addEventListener("DOMContentLoaded", function () {
    recorrer(document.documentElement);
    if (document.title) { var t = traducir(document.title); if (t) document.title = t; }
  });

  // Ventanas del navegador (confirm, alert, prompt) también en inglés
  var c = window.confirm, a = window.alert, p = window.prompt;
  window.confirm = function (m) { return c.call(window, window.ccT(m)); };
  window.alert = function (m) { return a.call(window, window.ccT(m)); };
  window.prompt = function (m, d) { return p.call(window, window.ccT(m), d); };
})();
