"""Conversaciones guardadas con la IA: listar, buscar, abrir, renombrar, fijar y borrar."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import or_

from models import AIConversation, AIMessage, db, utcnow
from utilidades import api_error, json_body

bp = Blueprint("conversaciones", __name__)
MAX_CONVERSACIONES = 500


def _dto(c, con_mensajes=False):
    d = {"id": c.id, "titulo": c.titulo, "fijada": c.fijada, "creada": c.creada.isoformat(), "actualizada": c.actualizada.isoformat()}
    if con_mensajes:
        d["mensajes"] = [{"id": m.id, "rol": m.rol, "texto": m.texto, "archivos": m.archivos or [], "creado": m.creado.isoformat()} for m in c.mensajes]
    return d


def propia(cid):
    return AIConversation.query.filter_by(id=cid, usuario_id=current_user.id).first() if cid else None


def titulo_de(texto):
    t = " ".join(str(texto or "").split())
    return (t[:57].rstrip() + "…") if len(t) > 58 else (t or "Archivos adjuntos")


def guardar_intercambio(conv, pregunta, archivos, respuesta):
    """Guarda la pregunta y la respuesta; la primera pregunta pone el título (como Claude)."""
    if not conv.mensajes and conv.titulo in ("", "Conversación nueva"):
        conv.titulo = titulo_de(pregunta)
    db.session.add(AIMessage(conversacion=conv, rol="yo", texto=pregunta or "(archivos)", archivos=list(archivos)[:20]))
    db.session.add(AIMessage(conversacion=conv, rol="tutor", texto=respuesta))
    conv.actualizada = utcnow()
    db.session.commit()


@bp.get("/api/ia/conversaciones/")
@login_required
def listar():
    q = AIConversation.query.filter_by(usuario_id=current_user.id).filter(AIConversation.mensajes.any())   # sin las vacías
    buscar = str(request.args.get("q", "")).strip()[:80]
    if buscar:
        patron = f"%{buscar}%"
        q = q.filter(or_(AIConversation.titulo.ilike(patron),
                         AIConversation.id.in_(db.session.query(AIMessage.conversacion_id).filter(AIMessage.texto.ilike(patron)))))
    filas = q.order_by(AIConversation.fijada.desc(), AIConversation.actualizada.desc()).limit(200).all()
    return jsonify(conversaciones=[_dto(c) for c in filas])


@bp.post("/api/ia/conversaciones/")
@login_required
def crear():
    data = json_body()
    if isinstance(data, tuple):
        return data
    if AIConversation.query.filter_by(usuario_id=current_user.id).count() >= MAX_CONVERSACIONES:
        return api_error(f"Tienes {MAX_CONVERSACIONES} conversaciones. Borra algunas para crear más.")
    c = AIConversation(usuario_id=current_user.id, titulo=titulo_de(data.get("titulo")) if data.get("titulo") else "Conversación nueva")
    db.session.add(c)
    db.session.flush()
    # Importar una conversación anterior (la que estaba guardada solo en el navegador)
    for m in (data.get("mensajes") or [])[:200]:
        if isinstance(m, dict) and m.get("rol") in ("yo", "tutor") and str(m.get("texto", "")).strip():
            db.session.add(AIMessage(conversacion=c, rol=m["rol"], texto=str(m["texto"])[:60000],
                                     archivos=[str(x)[:160] for x in (m.get("archivos") or [])][:20]))
    db.session.commit()
    return jsonify(conversacion=_dto(c, True)), 201


@bp.get("/api/ia/conversaciones/<int:cid>")
@login_required
def ver(cid):
    c = propia(cid)
    return jsonify(conversacion=_dto(c, True)) if c else api_error("Esa conversación no existe.", 404)


@bp.patch("/api/ia/conversaciones/<int:cid>")
@login_required
def editar(cid):
    c = propia(cid)
    if not c:
        return api_error("Esa conversación no existe.", 404)
    data = json_body()
    if isinstance(data, tuple):
        return data
    if "titulo" in data:
        t = " ".join(str(data["titulo"]).split())[:120]
        if not t:
            return api_error("El título no puede quedar vacío.")
        c.titulo = t
    if "fijada" in data:
        c.fijada = bool(data["fijada"])
    db.session.commit()
    return jsonify(conversacion=_dto(c))


@bp.delete("/api/ia/conversaciones/<int:cid>")
@login_required
def borrar(cid):
    c = propia(cid)
    if not c:
        return api_error("Esa conversación no existe.", 404)
    db.session.delete(c)
    db.session.commit()
    return jsonify(ok=True)
