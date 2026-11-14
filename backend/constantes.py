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
    {"clave": "xp30", "icono": "⭐", "titulo": "Gana 30 XP", "campo": "xp", "meta": 30, "premio": {"diamante": 1}},
    {"clave": "niveles2", "icono": "🎯", "titulo": "Completa 2 niveles", "campo": "niveles", "meta": 2, "premio": {"diamante": 2}},
    {"clave": "perfecto", "icono": "💎", "titulo": "Termina un nivel sin fallos", "campo": "perfectos", "meta": 1, "premio": {"diamante": 1}},
    {"clave": "xp60", "icono": "⭐", "titulo": "Gana 60 XP", "campo": "xp", "meta": 60, "premio": {"diamante": 1}},
    {"clave": "niveles4", "icono": "🎯", "titulo": "Completa 4 niveles", "campo": "niveles", "meta": 4, "premio": {"diamante": 1}},
    {"clave": "perfectos3", "icono": "💎", "titulo": "Termina 3 niveles sin fallos", "campo": "perfectos", "meta": 3, "premio": {"diamante": 1}},
]
PREMIO_MES = {"diamante": 5}
# Artículos que se pagan con diamantes. Se crean solos en la base la primera vez que se abre la tienda.
# tipo: "consumible" (se puede comprar muchas veces) o "permanente" (se compra una vez y queda en tu colección)
ARTICULOS_DIAMANTE = [
    {"clave": "impulso_xp", "nombre": "Impulso de XP", "icono": "⚡", "precio": 2, "rareza": "raro", "tipo": "consumible",
     "descripcion": "Gana 60 XP al instante y sube de nivel más rápido."},
    {"clave": "mega_vidas", "nombre": "Mega pack de vidas", "icono": "🔋", "precio": 4, "rareza": "raro", "tipo": "consumible",
     "descripcion": "Llena tus vidas hasta diez. ¡Practica sin parar!"},
    {"clave": "cofre_misterioso", "nombre": "Cofre misterioso", "icono": "📦", "precio": 2, "rareza": "raro", "tipo": "consumible",
     "descripcion": "Ábrelo y descubre un premio sorpresa: XP, vidas o más diamantes."},
    {"clave": "cofre_legendario", "nombre": "Cofre legendario", "icono": "🎁", "precio": 5, "rareza": "legendario", "tipo": "consumible",
     "descripcion": "Premio grande garantizado: 150 XP, 3 vidas y a veces diamantes extra."},
    {"clave": "gafas_pro", "nombre": "Gafas de programador", "icono": "😎", "precio": 2, "rareza": "comun", "tipo": "permanente",
     "descripcion": "Presume tu estilo en la colección de tu perfil."},
    {"clave": "marco_dorado", "nombre": "Marco dorado", "icono": "🖼️", "precio": 3, "rareza": "raro", "tipo": "permanente",
     "descripcion": "Un marco brillante para tu colección."},
    {"clave": "estela_cohete", "nombre": "Estela de cohete", "icono": "🚀", "precio": 3, "rareza": "raro", "tipo": "permanente",
     "descripcion": "Deja una estela de fuego por donde pases."},
    {"clave": "aura_neon", "nombre": "Aura neón", "icono": "🌈", "precio": 5, "rareza": "epico", "tipo": "permanente",
     "descripcion": "Un resplandor de colores que solo tienen los mejores."},
    {"clave": "corona_campeon", "nombre": "Corona de campeón", "icono": "👑", "precio": 6, "rareza": "epico", "tipo": "permanente",
     "descripcion": "La corona de quien no se rinde."},
    {"clave": "mascota_dragon", "nombre": "Mascota dragón", "icono": "🐉", "precio": 8, "rareza": "legendario", "tipo": "permanente",
     "descripcion": "Un dragón que cuida tu código."},
    {"clave": "titulo_leyenda", "nombre": "Título: Leyenda del código", "icono": "🌟", "precio": 10, "rareza": "legendario", "tipo": "permanente",
     "descripcion": "El título más raro de CódigoCamp."},
]
RAREZA = {"vida": "comun", "vidas_llenas": "comun", "salvarracha": "raro", "kit_experto": "raro",
          **{a["clave"]: a["rareza"] for a in ARTICULOS_DIAMANTE}}
PERMANENTES = {a["clave"] for a in ARTICULOS_DIAMANTE if a["tipo"] == "permanente"}
BASICOS_DIAMANTE = {"vida": 1, "vidas_llenas": 3, "salvarracha": 2, "kit_experto": 4}   # clave -> precio en diamantes
AVATARES_LIBRES = ["🙂", "😎", "🤖", "🦊", "🐱", "🐼", "🦄", "👾", "🐸", "🦉"]
ALIAS_OK = re.compile(r"^[a-z0-9_]{3,20}$")
