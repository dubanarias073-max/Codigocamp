"""Tienda de diamantes: ver artículos y comprar."""
import random

from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from models import Profile, Purchase, StoreItem, db
from constantes import MAX_SALVARRACHAS, MAX_VIDAS, MAX_VIDAS_REGEN, PERMANENTES, RAREZA
from servicios.perfil import apply_reward, get_profile, refresh_lives, reward_text
from servicios.tienda import asegurar_articulos
from cosmeticos import POR_CLAVE as COSMETICOS
from models import OwnedCosmetic
from utilidades import api_error, json_body

bp = Blueprint("tienda", __name__)


@bp.get("/api/tienda/")
@login_required
def tienda():
    asegurar_articulos()
    profile = get_profile(current_user)
    refresh_lives(profile)
    db.session.commit()
    tuyos = ({c.articulo.clave for c in Purchase.query.filter_by(usuario_id=current_user.id).all()} & PERMANENTES) | {c.clave for c in OwnedCosmetic.query.filter_by(usuario_id=current_user.id).all()}
    return jsonify(
        items=[{
            "clave": item.clave, "nombre": item.nombre, "descripcion": item.descripcion,
            "icono": item.icono, "precio": item.precio, "moneda": item.moneda,
            "categoria": item.categoria, "rareza": RAREZA.get(item.clave, "comun"),
            "permanente": item.clave in PERMANENTES, "tuyo": item.clave in tuyos,
            "tipo": COSMETICOS[item.clave]["tipo"] if item.clave in COSMETICOS else ("cofre" if item.clave.startswith("cofre") else "avatar" if item.clave in PERMANENTES else "potenciador"),
        } for item in StoreItem.query.filter_by(activo=True).order_by(StoreItem.orden).all()],
        minerales={"diamante": profile.diamante},
        xp=profile.xp, vidas=profile.vidas, salvarrachas=profile.salvarrachas,
    )


@bp.post("/api/tienda/comprar/")
@login_required
def tienda_comprar():
    data = json_body()
    if isinstance(data, tuple):
        return data
    asegurar_articulos()
    item = StoreItem.query.filter_by(clave=str(data.get("clave", "")), activo=True).first()
    if not item:
        return api_error("Ese artículo no existe.", 404)
    get_profile(current_user)
    profile = Profile.query.filter_by(usuario_id=current_user.id).with_for_update().one()
    refresh_lives(profile)
    if profile.diamante < item.precio:
        return api_error("No tienes suficientes diamantes.")
    if item.clave == "vida" and profile.vidas >= MAX_VIDAS:
        return api_error("Ya tienes el máximo de vidas.")
    if item.clave == "vidas_llenas" and profile.vidas >= MAX_VIDAS_REGEN:
        return api_error("Tus vidas ya están llenas.")
    if item.clave == "salvarracha" and profile.salvarrachas >= MAX_SALVARRACHAS:
        return api_error("Ya tienes el máximo de salvarrachas.")
    if item.clave == "kit_experto" and (profile.vidas >= MAX_VIDAS and profile.salvarrachas >= MAX_SALVARRACHAS):   # en la tienda el tope es 2
        return api_error("Ya tienes el máximo de vidas y salvarrachas.")
    if item.clave in COSMETICOS and OwnedCosmetic.query.filter_by(usuario_id=current_user.id, clave=item.clave).first():
        return api_error("Ya tienes este artículo en tu colección.")
    if item.clave in PERMANENTES and any(c.articulo_id == item.id for c in Purchase.query.filter_by(usuario_id=current_user.id).all()):
        return api_error("Ya tienes este artículo en tu colección.")
    if item.clave == "mega_vidas" and profile.vidas >= MAX_VIDAS:
        return api_error("Ya tienes el máximo de vidas.")
    profile.diamante -= item.precio
    premio = None
    if item.clave == "impulso_xp":
        premio = {"xp": 60}
    elif item.clave == "mega_vidas":
        profile.vidas = MAX_VIDAS
    elif item.clave == "cofre_misterioso":
        premio = random.choice([{"xp": 40}, {"xp": 80}, {"xp": 120}, {"vidas": 2}, {"vidas": 3}, {"diamante": 10}, {"diamante": 40}])
    elif item.clave == "cofre_legendario":
        premio = {"xp": 150, "vidas": 3}
        if random.random() < 0.3:
            premio["diamante"] = 3
    if premio:
        apply_reward(profile, premio)
    if item.clave == "vida":
        profile.vidas += 1
    elif item.clave == "vidas_llenas":
        profile.vidas = MAX_VIDAS_REGEN
    elif item.clave == "salvarracha":
        profile.salvarrachas += 1
    elif item.clave == "kit_experto":
        profile.vidas = min(MAX_VIDAS, profile.vidas + 3)
        profile.salvarrachas = max(profile.salvarrachas, min(MAX_SALVARRACHAS, profile.salvarrachas + 1))
    db.session.add(Purchase(usuario_id=current_user.id, articulo=item, precio=item.precio, moneda="diamante"))
    if item.clave in COSMETICOS:
        db.session.add(OwnedCosmetic(usuario_id=current_user.id, clave=item.clave, origen="tienda"))
    db.session.commit()
    return jsonify(
        ok=True, minerales={"diamante": profile.diamante},
        xp=profile.xp, vidas=profile.vidas, salvarrachas=profile.salvarrachas,
        premio=reward_text(premio) if premio else None,
    )
