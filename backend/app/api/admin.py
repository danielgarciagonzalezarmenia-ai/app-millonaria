"""Endpoints de administración para gestionar pronósticos.

Solo accesibles para usuarios con rol admin (UID en ADMIN_UIDS o claim admin=true).
"""

from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import FirebaseUser, get_current_user, is_admin
from app.core import firebase
from app.models import Prediction, PredictionPublic, TrendType

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _require_admin(user: FirebaseUser = Depends(get_current_user)) -> FirebaseUser:
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Solo administradores.")
    return user


def _to_public(doc: dict) -> PredictionPublic:
    doc = dict(doc)
    doc["market_type"] = doc.get("market_type", "other")
    doc["basis"] = doc.get("basis", [])
    return PredictionPublic(**doc)


@router.get("/predictions", response_model=list[PredictionPublic])
async def list_all_predictions(user: FirebaseUser = Depends(_require_admin)):
    """Lista todos los pronósticos activos (gratis + premium)."""
    db = firebase.db()
    docs = (
        db.collection("predictions")
        .where("status", "==", "active")
        .order_by("created_at", direction="DESCENDING")
        .limit(200)
        .get()
    )
    return [_to_public(s.to_dict()) for s in docs]


class PredictionBody(Prediction):
    """Body para crear/editar pronóstico (hereda todos los campos de Prediction)."""
    pass


@router.post("/predictions", response_model=PredictionPublic)
async def create_prediction(
    body: PredictionBody,
    user: FirebaseUser = Depends(_require_admin),
):
    """Crea un pronóstico nuevo."""
    db = firebase.db()
    doc_id = f"{body.match_id}_{body.selection}"
    doc_ref = db.collection("predictions").document(doc_id)

    existing = doc_ref.get()
    if existing.exists:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un pronóstico con ID {doc_id}. Usa PUT para editar.",
        )

    data = body.model_dump()
    data["created_at"] = dt.datetime.now(dt.timezone.utc)
    data["status"] = "active"
    doc_ref.set(data)

    return _to_public(data)


@router.put("/predictions/{doc_id:path}", response_model=PredictionPublic)
async def update_prediction(
    doc_id: str,
    body: PredictionBody,
    user: FirebaseUser = Depends(_require_admin),
):
    """Actualiza un pronóstico existente por su doc_id (match_id_selection)."""
    db = firebase.db()
    doc_ref = db.collection("predictions").document(doc_id)

    existing = doc_ref.get()
    if not existing.exists:
        raise HTTPException(status_code=404, detail="Pronóstico no encontrado.")

    data = body.model_dump()
    data["status"] = "active"
    doc_ref.set(data, merge=True)

    return _to_public(data)


@router.delete("/predictions/{doc_id:path}")
async def delete_prediction(
    doc_id: str,
    user: FirebaseUser = Depends(_require_admin),
):
    """Elimina un pronóstico (marca status=inactive)."""
    db = firebase.db()
    doc_ref = db.collection("predictions").document(doc_id)

    existing = doc_ref.get()
    if not existing.exists:
        raise HTTPException(status_code=404, detail="Pronóstico no encontrado.")

    doc_ref.update({"status": "inactive"})
    return {"detail": "Pronóstico eliminado.", "doc_id": doc_id}
