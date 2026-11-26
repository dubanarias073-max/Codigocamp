"""Constantes del juego: vidas, premios, desafíos, artículos de la tienda y avatares."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
BACKEND = Path(__file__).resolve().parent

MAX_VIDAS_REGEN = 5
MAX_VIDAS = 10
MAX_SALVARRACHAS = 2            # tope para comprarlos en la tienda o sacarlos de los cofres del camino
MAX_SALVARRACHAS_PREMIO = 10    # los que se ganan con la racha sí pueden pasar de 2 (hasta este tope)
SALVARRACHAS_CADA = 10          # cada 10 días seguidos de racha: +1 salvarrachas de regalo
PREMIO_SEMANA_PERFECTA = {"diamante": 250, "xp": 100, "salvarrachas": 1}
PREMIO_MES_PERFECTO = {"diamante": 2000, "xp": 600, "vidas": 10, "salvarrachas": 3}
MINUTOS_VIDA = 30
META_MES = 150   # puntos del desafío del mes = 30 encargos (5 puntos cada uno), como el de Duolingo
PUNTOS_POR_DESAFIO = 5
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
# Encargos de hoy: cada día salen 7 distintos de esta lista (cambian cada día y para cada persona; ver encargos_del_dia).
ENCARGOS = [
    {"clave": "xp20", "icono": "⭐", "titulo": "Gana 20 XP", "campo": "xp", "meta": 20, "premio": {"diamante": 8}},
    {"clave": "xp30", "icono": "⭐", "titulo": "Gana 30 XP", "campo": "xp", "meta": 30, "premio": {"diamante": 10}},
    {"clave": "xp50", "icono": "⭐", "titulo": "Gana 50 XP", "campo": "xp", "meta": 50, "premio": {"diamante": 15}},
    {"clave": "xp80", "icono": "🌟", "titulo": "Gana 80 XP", "campo": "xp", "meta": 80, "premio": {"diamante": 20}},
    {"clave": "xp120", "icono": "🌟", "titulo": "Gana 120 XP", "campo": "xp", "meta": 120, "premio": {"diamante": 30}},
    {"clave": "niveles1", "icono": "🎯", "titulo": "Completa 1 nivel de retos", "campo": "niveles", "meta": 1, "premio": {"diamante": 8}},
    {"clave": "niveles2", "icono": "🎯", "titulo": "Completa 2 niveles", "campo": "niveles", "meta": 2, "premio": {"diamante": 15}},
    {"clave": "niveles3", "icono": "🎯", "titulo": "Completa 3 niveles", "campo": "niveles", "meta": 3, "premio": {"diamante": 20}},
    {"clave": "niveles5", "icono": "🏹", "titulo": "Completa 5 niveles", "campo": "niveles", "meta": 5, "premio": {"diamante": 30}},
    {"clave": "perfecto", "icono": "💎", "titulo": "Termina un nivel sin fallos", "campo": "perfectos", "meta": 1, "premio": {"diamante": 12}},
    {"clave": "perfectos2", "icono": "💎", "titulo": "Termina 2 niveles sin fallos", "campo": "perfectos", "meta": 2, "premio": {"diamante": 18}},
    {"clave": "perfectos3", "icono": "💎", "titulo": "Termina 3 niveles sin fallos", "campo": "perfectos", "meta": 3, "premio": {"diamante": 25}},
    {"clave": "lecciones1", "icono": "📘", "titulo": "Completa 1 lección en Aprende", "campo": "lecciones", "meta": 1, "premio": {"diamante": 10}},
    {"clave": "lecciones2", "icono": "📘", "titulo": "Completa 2 lecciones en Aprende", "campo": "lecciones", "meta": 2, "premio": {"diamante": 15}},
    {"clave": "lecciones3", "icono": "📚", "titulo": "Completa 3 lecciones en Aprende", "campo": "lecciones", "meta": 3, "premio": {"diamante": 20}},
    {"clave": "lecciones5", "icono": "📚", "titulo": "Completa 5 lecciones en Aprende", "campo": "lecciones", "meta": 5, "premio": {"diamante": 30}},
    {"clave": "mensajes1", "icono": "💬", "titulo": "Escríbele a un amigo en Chats", "campo": "mensajes", "meta": 1, "premio": {"diamante": 8}},
    {"clave": "mensajes5", "icono": "💬", "titulo": "Envía 5 mensajes en Chats", "campo": "mensajes", "meta": 5, "premio": {"diamante": 12}},
    {"clave": "ia1", "icono": "🤖", "titulo": "Pregúntale algo al tutor de IA", "campo": "ia", "meta": 1, "premio": {"diamante": 8}},
    {"clave": "ia3", "icono": "🤖", "titulo": "Hazle 3 preguntas al tutor de IA", "campo": "ia", "meta": 3, "premio": {"diamante": 12}},
    {"clave": "codigo1", "icono": "▶️", "titulo": "Ejecuta tu código en Trabajo", "campo": "ejecuciones", "meta": 1, "premio": {"diamante": 8}},
    {"clave": "codigo5", "icono": "▶️", "titulo": "Ejecuta tu código 5 veces en Trabajo", "campo": "ejecuciones", "meta": 5, "premio": {"diamante": 15}},
    {"clave": "combo", "icono": "⚡", "titulo": "Gana 40 XP y completa 2 niveles", "campo": "xp", "meta": 40, "y": {"campo": "niveles", "meta": 2}, "premio": {"diamante": 25}},
    {"clave": "estudioso", "icono": "🧠", "titulo": "Haz 1 lección en Aprende y 1 nivel de retos", "campo": "lecciones", "meta": 1, "y": {"campo": "niveles", "meta": 1}, "premio": {"diamante": 18}},
    {"clave": "maraton", "icono": "🔥", "titulo": "Maratón: completa 8 niveles", "campo": "niveles", "meta": 8, "premio": {"diamante": 45}},
    # --- Más encargos (variados: premios con XP, vidas y salvarrachas, no solo diamantes) ---
    {"clave": "xp15", "icono": "✨", "titulo": "Calentamiento: gana 15 XP", "campo": "xp", "meta": 15, "premio": {"diamante": 6, "xp": 5}},
    {"clave": "xp60", "icono": "⭐", "titulo": "Gana 60 XP", "campo": "xp", "meta": 60, "premio": {"diamante": 18}},
    {"clave": "xp100", "icono": "🌟", "titulo": "Gana 100 XP", "campo": "xp", "meta": 100, "premio": {"diamante": 25, "vidas": 1}},
    {"clave": "xp150", "icono": "💫", "titulo": "Día brillante: gana 150 XP", "campo": "xp", "meta": 150, "premio": {"diamante": 35, "vidas": 2}},
    {"clave": "xp200", "icono": "🚀", "titulo": "Despegue: gana 200 XP", "campo": "xp", "meta": 200, "premio": {"diamante": 50, "salvarrachas": 1}},
    {"clave": "niveles4", "icono": "🎯", "titulo": "Completa 4 niveles", "campo": "niveles", "meta": 4, "premio": {"diamante": 25}},
    {"clave": "niveles6", "icono": "🏹", "titulo": "Completa 6 niveles", "campo": "niveles", "meta": 6, "premio": {"diamante": 35, "vidas": 1}},
    {"clave": "niveles10", "icono": "🏆", "titulo": "Superhéroe: completa 10 niveles", "campo": "niveles", "meta": 10, "premio": {"diamante": 60, "salvarrachas": 1}},
    {"clave": "perfectos4", "icono": "💎", "titulo": "Perfección: 4 niveles sin fallos", "campo": "perfectos", "meta": 4, "premio": {"diamante": 32, "vidas": 1}},
    {"clave": "perfectos5", "icono": "👑", "titulo": "Sin errores: 5 niveles perfectos", "campo": "perfectos", "meta": 5, "premio": {"diamante": 40, "xp": 20}},
    {"clave": "lecciones4", "icono": "📚", "titulo": "Completa 4 lecciones en Aprende", "campo": "lecciones", "meta": 4, "premio": {"diamante": 25}},
    {"clave": "lecciones8", "icono": "🎓", "titulo": "Biblioteca: 8 lecciones en Aprende", "campo": "lecciones", "meta": 8, "premio": {"diamante": 45, "vidas": 2}},
    {"clave": "mensajes3", "icono": "💬", "titulo": "Envía 3 mensajes a tus amigos", "campo": "mensajes", "meta": 3, "premio": {"diamante": 10}},
    {"clave": "mensajes10", "icono": "🗨️", "titulo": "Conversador: envía 10 mensajes", "campo": "mensajes", "meta": 10, "premio": {"diamante": 18, "xp": 10}},
    {"clave": "ia2", "icono": "🤖", "titulo": "Hazle 2 preguntas a Codi", "campo": "ia", "meta": 2, "premio": {"diamante": 10}},
    {"clave": "ia5", "icono": "🧠", "titulo": "Curioso: 5 preguntas al tutor de IA", "campo": "ia", "meta": 5, "premio": {"diamante": 18, "xp": 10}},
    {"clave": "codigo3", "icono": "▶️", "titulo": "Ejecuta tu código 3 veces en Trabajo", "campo": "ejecuciones", "meta": 3, "premio": {"diamante": 12}},
    {"clave": "codigo10", "icono": "🛠️", "titulo": "Constructor: ejecuta 10 veces en Trabajo", "campo": "ejecuciones", "meta": 10, "premio": {"diamante": 25, "xp": 15}},
    {"clave": "combo_ia", "icono": "🤝", "titulo": "Pregúntale a la IA y completa 2 niveles", "campo": "ia", "meta": 1, "y": {"campo": "niveles", "meta": 2}, "premio": {"diamante": 20}},
    {"clave": "combo_trabajo", "icono": "💻", "titulo": "Haz 1 lección y ejecuta tu código", "campo": "lecciones", "meta": 1, "y": {"campo": "ejecuciones", "meta": 1}, "premio": {"diamante": 18}},
    {"clave": "combo_social", "icono": "👥", "titulo": "Escribe a un amigo y completa 1 nivel", "campo": "mensajes", "meta": 1, "y": {"campo": "niveles", "meta": 1}, "premio": {"diamante": 15}},
    {"clave": "combo_perfecto", "icono": "🌈", "titulo": "Gana 60 XP con 2 niveles perfectos", "campo": "xp", "meta": 60, "y": {"campo": "perfectos", "meta": 2}, "premio": {"diamante": 35, "vidas": 1}},
    {"clave": "combo_sabio", "icono": "🦉", "titulo": "Haz 2 lecciones y 1 nivel perfecto", "campo": "lecciones", "meta": 2, "y": {"campo": "perfectos", "meta": 1}, "premio": {"diamante": 28}},
    {"clave": "combo_xp_aprende", "icono": "📖", "titulo": "Gana 50 XP y haz 3 lecciones", "campo": "xp", "meta": 50, "y": {"campo": "lecciones", "meta": 3}, "premio": {"diamante": 30}},
    {"clave": "super_maraton", "icono": "🌋", "titulo": "Súper maratón: completa 12 niveles", "campo": "niveles", "meta": 12, "premio": {"diamante": 80, "salvarrachas": 1, "vidas": 3}},
    {"clave": "xp300", "icono": "☄️", "titulo": "Leyenda del día: gana 300 XP", "campo": "xp", "meta": 300, "premio": {"diamante": 90, "salvarrachas": 1}},
]
ENCARGOS_POR_CLAVE = {e["clave"]: e for e in ENCARGOS}
ENCARGOS_POR_DIA = 7
# Compatibilidad (código y pruebas viejas): la lista de antes
DAILY_CHALLENGES = [ENCARGOS_POR_CLAVE[k] for k in ("xp30", "niveles2", "perfecto", "xp50", "niveles3", "perfectos3")]
PREMIO_MES = {"diamante": 150}
# Artículos que se pagan con diamantes. Se crean solos en la base la primera vez que se abre la tienda.
# tipo: "consumible" (se puede comprar muchas veces) o "permanente" (se compra una vez y queda en tu colección)
ARTICULOS_DIAMANTE = [
    {"clave": "impulso_xp", "nombre": "Impulso de XP", "icono": "⚡", "precio": 40, "rareza": "raro", "tipo": "consumible",
     "descripcion": "Gana 60 XP al instante y sube de nivel más rápido."},
    {"clave": "mega_vidas", "nombre": "Mega pack de vidas", "icono": "🔋", "precio": 60, "rareza": "raro", "tipo": "consumible",
     "descripcion": "Llena tus vidas hasta diez. ¡Practica sin parar!"},
    {"clave": "cofre_misterioso", "nombre": "Cofre misterioso", "icono": "📦", "precio": 35, "rareza": "raro", "tipo": "consumible",
     "descripcion": "Ábrelo y descubre un premio sorpresa: XP, vidas o más diamantes."},
    {"clave": "cofre_legendario", "nombre": "Cofre legendario", "icono": "🎁", "precio": 120, "rareza": "legendario", "tipo": "consumible",
     "descripcion": "Premio grande garantizado: 150 XP, 3 vidas y a veces diamantes extra."},
]
RAREZA = {"vida": "comun", "vidas_llenas": "comun", "salvarracha": "raro", "kit_experto": "raro",
          **{a["clave"]: a["rareza"] for a in ARTICULOS_DIAMANTE}}
PERMANENTES = {a["clave"] for a in ARTICULOS_DIAMANTE if a["tipo"] == "permanente"}
from cosmeticos import COSMETICOS as _COSMETICOS, EN_TIENDA as _EN_TIENDA  # noqa: E402
PERMANENTES |= {c["clave"] for c in _COSMETICOS}
RAREZA.update({c["clave"]: c["rareza"] for c in _COSMETICOS})
COSMETICOS_TIENDA = _EN_TIENDA
BASICOS_DIAMANTE = {"vida": 10, "vidas_llenas": 30, "salvarracha": 50, "kit_experto": 45}   # clave -> precio en diamantes
# Avatares retirados (antes se vendían en la tienda): sus compras se devuelven en diamantes (migración «quitar_avatares»).
AVATARES_RETIRADOS = {"gafas_pro", "marco_dorado", "estela_cohete", "aura_neon", "corona_campeon", "mascota_dragon", "titulo_leyenda"}
AVATARES_LIBRES = ["zorro", "gato", "panda", "buho", "robot", "rana", "alien", "unicor", "pulpo", "tigre"]   # dibujos en frontend/js/avatares.js
# Avatares de antes (emojis) → los nuevos dibujos
AVATAR_DE_EMOJI = {"🦊": "zorro", "🐱": "gato", "🐼": "panda", "🦉": "buho", "🤖": "robot", "🐸": "rana", "👾": "alien", "🦄": "unicor",
                   "😎": "gafas", "🖼️": "dorado", "🚀": "cohete", "🌈": "aura", "👑": "corona", "🐉": "dragon", "🌟": "leyenda"}
ALIAS_OK = re.compile(r"^[a-z0-9_]{3,20}$")
