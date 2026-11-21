"""Cosméticos (fondos de página, punteros, temas de color, marcos de foto, efectos y estelas del dedo) y los 10 cofres.

El aspecto de cada cosmético vive en frontend/js/cosmeticos.js; aquí solo su clave, tipo, precio y rareza.
Los «exclusivos» no se venden: solo salen de los cofres.
"""

TIPOS = ("fondo", "cursor", "tema", "marco", "efecto", "dedo")

COSMETICOS = [
    # ---- Fondos de página
    {"clave": "fondo_aurora", "tipo": "fondo", "nombre": "Aurora boreal", "precio": 320, "rareza": "raro", "descripcion": "Luces del norte que se mueven despacio detrás de todo."},
    {"clave": "fondo_galaxia", "tipo": "fondo", "nombre": "Galaxia", "precio": 650, "rareza": "epico", "descripcion": "Estrellas que titilan sobre una nebulosa violeta."},
    {"clave": "fondo_matrix", "tipo": "fondo", "nombre": "Lluvia de código", "precio": 900, "rareza": "epico", "descripcion": "Columnas de código verde cayendo, como en las películas de hackers."},
    {"clave": "fondo_synthwave", "tipo": "fondo", "nombre": "Synthwave", "precio": 700, "rareza": "epico", "descripcion": "Sol retro y cuadrícula neón al estilo de los 80."},
    {"clave": "fondo_oceano", "tipo": "fondo", "nombre": "Océano", "precio": 260, "rareza": "raro", "descripcion": "Olas suaves en tonos azules."},
    {"clave": "fondo_circuito", "tipo": "fondo", "nombre": "Circuito", "precio": 240, "rareza": "raro", "descripcion": "Pistas de una placa electrónica."},
    {"clave": "fondo_atardecer", "tipo": "fondo", "nombre": "Atardecer", "precio": 80, "rareza": "comun", "descripcion": "Degradado cálido de naranja a rosa."},
    {"clave": "fondo_bosque", "tipo": "fondo", "nombre": "Bosque", "precio": 80, "rareza": "comun", "descripcion": "Verdes tranquilos para concentrarte."},
    # ---- Punteros del mouse
    {"clave": "cursor_cohete", "tipo": "cursor", "nombre": "Cohete", "precio": 180, "rareza": "raro", "descripcion": "Tu puntero es un cohete listo para despegar."},
    {"clave": "cursor_espada", "tipo": "cursor", "nombre": "Espada pixel", "precio": 220, "rareza": "raro", "descripcion": "Una espada de 8 bits para cortar bugs."},
    {"clave": "cursor_varita", "tipo": "cursor", "nombre": "Varita mágica", "precio": 450, "rareza": "epico", "descripcion": "Con una estrella en la punta."},
    {"clave": "cursor_lapiz", "tipo": "cursor", "nombre": "Lápiz", "precio": 60, "rareza": "comun", "descripcion": "Para escribir tu mejor código."},
    {"clave": "cursor_neon", "tipo": "cursor", "nombre": "Flecha neón", "precio": 160, "rareza": "raro", "descripcion": "Una flecha que brilla en cian."},
    {"clave": "cursor_gato", "tipo": "cursor", "nombre": "Patita de gato", "precio": 70, "rareza": "comun", "descripcion": "Miau."},
    # ---- Temas de color (botones, enlaces y acentos)
    {"clave": "tema_oceano", "tipo": "tema", "nombre": "Tema océano", "precio": 90, "rareza": "comun", "descripcion": "Acentos azules en toda la página."},
    {"clave": "tema_neon", "tipo": "tema", "nombre": "Tema neón", "precio": 260, "rareza": "raro", "descripcion": "Morado y rosa eléctrico."},
    {"clave": "tema_bosque", "tipo": "tema", "nombre": "Tema bosque", "precio": 90, "rareza": "comun", "descripcion": "Verdes naturales."},
    {"clave": "tema_atardecer", "tipo": "tema", "nombre": "Tema atardecer", "precio": 90, "rareza": "comun", "descripcion": "Naranjas y corales."},
    # ---- Marcos para la foto de perfil
    {"clave": "marco_neon", "tipo": "marco", "nombre": "Marco neón", "precio": 240, "rareza": "raro", "descripcion": "Un aro que brilla alrededor de tu foto."},
    {"clave": "marco_arcoiris", "tipo": "marco", "nombre": "Marco arcoíris", "precio": 600, "rareza": "epico", "descripcion": "Gira con todos los colores."},
    {"clave": "marco_oro", "tipo": "marco", "nombre": "Marco de oro", "precio": 800, "rareza": "epico", "descripcion": "Para los que van en serio."},
    # ---- Efectos
    {"clave": "efecto_burbujas", "tipo": "efecto", "nombre": "Burbujas al hacer clic", "precio": 200, "rareza": "raro", "descripcion": "Cada clic suelta burbujas."},
    {"clave": "efecto_confeti", "tipo": "efecto", "nombre": "Confeti al hacer clic", "precio": 550, "rareza": "epico", "descripcion": "Cada clic es una fiesta."},
    # ---- Premium (lo más bacano de la tienda: cuesta mucho)
    {"clave": "fondo_nieve", "tipo": "fondo", "nombre": "Noche nevada", "precio": 480, "rareza": "epico", "descripcion": "Copos de nieve que caen despacio sobre un cielo azul noche."},
    {"clave": "fondo_luciernagas", "tipo": "fondo", "nombre": "Luciérnagas", "precio": 520, "rareza": "epico", "descripcion": "Cientos de lucecitas que flotan y parpadean en el bosque."},
    {"clave": "fondo_ciudad", "tipo": "fondo", "nombre": "Ciudad neón", "precio": 750, "rareza": "epico", "descripcion": "Rascacielos con ventanas encendidas y un cielo violeta."},
    {"clave": "fondo_hiperespacio", "tipo": "fondo", "nombre": "Hiperespacio", "precio": 2500, "rareza": "legendario", "descripcion": "Viajas entre estrellas a la velocidad de la luz. Animado."},
    {"clave": "fondo_agujero_negro", "tipo": "fondo", "nombre": "Agujero negro", "precio": 3000, "rareza": "legendario", "descripcion": "Un remolino de luz que gira alrededor del vacío. Animado."},
    {"clave": "cursor_rayo", "tipo": "cursor", "nombre": "Rayo", "precio": 380, "rareza": "epico", "descripcion": "Un rayo eléctrico como puntero."},
    {"clave": "cursor_sable", "tipo": "cursor", "nombre": "Sable de energía", "precio": 950, "rareza": "epico", "descripcion": "Una hoja de luz cian que brilla."},
    {"clave": "cursor_diamante", "tipo": "cursor", "nombre": "Puntero de diamante", "precio": 1800, "rareza": "legendario", "descripcion": "Una flecha tallada en diamante."},
    {"clave": "tema_cyberpunk", "tipo": "tema", "nombre": "Tema cyberpunk", "precio": 420, "rareza": "epico", "descripcion": "Amarillo eléctrico y magenta."},
    {"clave": "tema_hielo", "tipo": "tema", "nombre": "Tema hielo", "precio": 300, "rareza": "raro", "descripcion": "Azules glaciares y blanco."},
    {"clave": "tema_lava", "tipo": "tema", "nombre": "Tema lava", "precio": 300, "rareza": "raro", "descripcion": "Rojos y naranjas volcánicos."},
    {"clave": "tema_galaxia", "tipo": "tema", "nombre": "Tema galaxia", "precio": 1500, "rareza": "legendario", "descripcion": "Violeta, rosa y cian de nebulosa."},
    {"clave": "marco_codigo", "tipo": "marco", "nombre": "Marco terminal", "precio": 350, "rareza": "raro", "descripcion": "Un aro verde de terminal que parpadea."},
    {"clave": "marco_hielo", "tipo": "marco", "nombre": "Marco de hielo", "precio": 700, "rareza": "epico", "descripcion": "Cristales de hielo alrededor de tu foto."},
    {"clave": "marco_plasma", "tipo": "marco", "nombre": "Marco de plasma", "precio": 2200, "rareza": "legendario", "descripcion": "Energía que gira sin parar alrededor de tu foto."},
    {"clave": "marco_diamante", "tipo": "marco", "nombre": "Marco de diamante", "precio": 3500, "rareza": "legendario", "descripcion": "El marco más caro de CódigoCamp: brilla como un diamante."},
    {"clave": "efecto_corazones", "tipo": "efecto", "nombre": "Corazones al hacer clic", "precio": 300, "rareza": "raro", "descripcion": "Cada clic suelta corazones."},
    {"clave": "efecto_monedas", "tipo": "efecto", "nombre": "Lluvia de monedas", "precio": 650, "rareza": "epico", "descripcion": "Cada clic hace saltar monedas de oro."},
    {"clave": "efecto_rayos", "tipo": "efecto", "nombre": "Descarga eléctrica", "precio": 800, "rareza": "epico", "descripcion": "Chispas eléctricas en cada clic."},
    {"clave": "efecto_fuegos", "tipo": "efecto", "nombre": "Fuegos artificiales", "precio": 2000, "rareza": "legendario", "descripcion": "Cada clic es un fuego artificial de colores."},
    # ---- Estelas del dedo (para el celular: siguen tu dedo al tocar y deslizar la pantalla)
    {"clave": "dedo_tinta", "tipo": "dedo", "nombre": "Tinta", "precio": 70, "rareza": "comun", "descripcion": "Gotas de tinta azul que siguen tu dedo."},
    {"clave": "dedo_burbujas", "tipo": "dedo", "nombre": "Burbujas", "precio": 90, "rareza": "comun", "descripcion": "Deslizas y salen burbujas que flotan hacia arriba."},
    {"clave": "dedo_neon", "tipo": "dedo", "nombre": "Trazo neón", "precio": 220, "rareza": "raro", "descripcion": "Una línea de luz cian que dibuja por donde pasas."},
    {"clave": "dedo_codigo", "tipo": "dedo", "nombre": "Rastro de código", "precio": 260, "rareza": "raro", "descripcion": "Caen llaves, etiquetas y ceros y unos al deslizar."},
    {"clave": "dedo_arcoiris", "tipo": "dedo", "nombre": "Arcoíris", "precio": 520, "rareza": "epico", "descripcion": "Tu dedo pinta una cinta con todos los colores."},
    {"clave": "dedo_fuego", "tipo": "dedo", "nombre": "Dedo de fuego", "precio": 680, "rareza": "epico", "descripcion": "Llamas y brasas que suben por donde tocas."},
    {"clave": "dedo_galaxia", "tipo": "dedo", "nombre": "Polvo de galaxia", "precio": 1900, "rareza": "legendario", "descripcion": "Estrellas y polvo cósmico de colores con cada toque."},
    # ---- Exclusivos de cofre (no se venden)
    {"clave": "cursor_estrella", "tipo": "cursor", "nombre": "Estrella fugaz", "precio": 0, "rareza": "raro", "exclusivo": True, "descripcion": "Exclusivo del cofre «Racha de 3 días»."},
    {"clave": "fondo_cuadricula", "tipo": "fondo", "nombre": "Cuadrícula neón", "precio": 0, "rareza": "raro", "exclusivo": True, "descripcion": "Exclusivo del cofre «100 XP»."},
    {"clave": "marco_fuego", "tipo": "marco", "nombre": "Marco de fuego", "precio": 0, "rareza": "epico", "exclusivo": True, "descripcion": "Exclusivo del cofre «Una semana»."},
    {"clave": "efecto_chispas", "tipo": "efecto", "nombre": "Chispas", "precio": 0, "rareza": "epico", "exclusivo": True, "descripcion": "Exclusivo del cofre «500 XP»."},
    {"clave": "tema_oro", "tipo": "tema", "nombre": "Tema dorado", "precio": 0, "rareza": "epico", "exclusivo": True, "descripcion": "Exclusivo del cofre «Constante»."},
    {"clave": "cursor_corona", "tipo": "cursor", "nombre": "Corona", "precio": 0, "rareza": "legendario", "exclusivo": True, "descripcion": "Exclusivo del cofre «Amigos»."},
    {"clave": "fondo_dragon", "tipo": "fondo", "nombre": "Dragón de fuego", "precio": 0, "rareza": "legendario", "exclusivo": True, "descripcion": "Exclusivo del cofre «Un mes»."},
    {"clave": "marco_legendario", "tipo": "marco", "nombre": "Marco legendario", "precio": 0, "rareza": "legendario", "exclusivo": True, "descripcion": "Exclusivo del cofre «Leyenda»."},
    {"clave": "efecto_estela", "tipo": "efecto", "nombre": "Estela de estrellas", "precio": 0, "rareza": "legendario", "exclusivo": True, "descripcion": "Tu puntero deja estrellas. Exclusivo del cofre «Leyenda»."},
]
POR_CLAVE = {c["clave"]: c for c in COSMETICOS}
EN_TIENDA = [c for c in COSMETICOS if not c.get("exclusivo")]

# Los 10 cofres: (clave, nombre, tipo de cofre, qué medir, meta, premio)
COFRES = [
    {"clave": "c01_primer_paso", "nombre": "Primer paso", "cofre": "madera", "medida": "lecciones", "meta": 1, "texto": "Completa tu primera lección", "premio": {"diamante": 50, "vidas": 2}},
    {"clave": "c02_racha3", "nombre": "Racha de 3 días", "cofre": "madera", "medida": "racha", "meta": 3, "texto": "Practica 3 días seguidos", "premio": {"diamante": 80, "cosmetico": "cursor_estrella"}},
    {"clave": "c03_xp100", "nombre": "100 XP", "cofre": "plata", "medida": "xp", "meta": 100, "texto": "Gana 100 XP", "premio": {"diamante": 120, "cosmetico": "fondo_cuadricula"}},
    {"clave": "c04_retador", "nombre": "Retador", "cofre": "plata", "medida": "niveles", "meta": 10, "texto": "Supera 10 niveles de retos", "premio": {"diamante": 150, "salvarrachas": 1}},
    {"clave": "c05_semana", "nombre": "Una semana", "cofre": "oro", "medida": "racha", "meta": 7, "texto": "Practica 7 días seguidos", "premio": {"diamante": 200, "cosmetico": "marco_fuego"}},
    {"clave": "c06_xp500", "nombre": "500 XP", "cofre": "oro", "medida": "xp", "meta": 500, "texto": "Gana 500 XP", "premio": {"diamante": 250, "cosmetico": "efecto_chispas"}},
    {"clave": "c07_constante", "nombre": "Constante", "cofre": "oro", "medida": "desafios", "meta": 15, "texto": "Supera 15 encargos diarios", "premio": {"diamante": 300, "cosmetico": "tema_oro"}},
    {"clave": "c08_amigos", "nombre": "Amigos", "cofre": "diamante", "medida": "amigos", "meta": 1, "texto": "Agrega a un amigo en Chats", "premio": {"diamante": 400, "cosmetico": "cursor_corona"}},
    {"clave": "c09_mes", "nombre": "Un mes", "cofre": "diamante", "medida": "racha", "meta": 30, "texto": "Practica 30 días seguidos", "premio": {"diamante": 600, "salvarrachas": 2, "cosmetico": "fondo_dragon"}},
    {"clave": "c10_leyenda", "nombre": "Leyenda", "cofre": "legendario", "medida": "xp", "meta": 2000, "texto": "Gana 2000 XP", "premio": {"diamante": 1000, "cosmetico": ["marco_legendario", "efecto_estela"]}},
]
COFRE_POR_CLAVE = {c["clave"]: c for c in COFRES}
