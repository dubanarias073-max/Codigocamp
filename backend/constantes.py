"""Constantes del juego: vidas, premios, desafíos, artículos de la tienda y avatares."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
BACKEND = Path(__file__).resolve().parent

MAX_VIDAS_REGEN = 5
MAX_VIDAS = 10
MAX_SALVARRACHAS = 2
MINUTOS_VIDA = 30
META_MES = 60
PUNTOS_POR_DESAFIO = 5
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DAILY_CHALLENGES = [
    {"clave": "xp30", "icono": "⭐", "titulo": "Gana 30 XP", "campo": "xp", "meta": 30, "premio": {"diamante": 10}},
    {"clave": "niveles2", "icono": "🎯", "titulo": "Completa 2 niveles", "campo": "niveles", "meta": 2, "premio": {"diamante": 20}},
    {"clave": "perfecto", "icono": "💎", "titulo": "Termina un nivel sin fallos", "campo": "perfectos", "meta": 1, "premio": {"diamante": 15}},
    {"clave": "xp60", "icono": "⭐", "titulo": "Gana 60 XP", "campo": "xp", "meta": 60, "premio": {"diamante": 15}},
    {"clave": "niveles4", "icono": "🎯", "titulo": "Completa 4 niveles", "campo": "niveles", "meta": 4, "premio": {"diamante": 20}},
    {"clave": "perfectos3", "icono": "💎", "titulo": "Termina 3 niveles sin fallos", "campo": "perfectos", "meta": 3, "premio": {"diamante": 20}},
]
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
