"""Endpoints de pronósticos.

- /api/predictions        -> todos (hoy + historial), gratis para todos;
                             premium solo si el usuario tiene suscripción activa.
- /api/predictions/today  -> solo los del día (hora de Colombia), gratis primeros.
- /api/predictions/history-> días anteriores (historial).
- /api/predictions/{id}   -> detalle de un pronóstico (mismo gating).
"""

from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.auth import get_optional_user
from app.core import firebase
from app.models import PredictionPublic

router = APIRouter(prefix="/api/predictions", tags=["predictions"])

COLOMBIA_TZ = ZoneInfo("America/Bogota")


def _to_public(doc: dict) -> PredictionPublic:
    # Coercion de tipos para safe serialization.
    doc = dict(doc)
    doc["market_type"] = doc.get("market_type", "other")
    doc["basis"] = doc.get("basis", [])
    return PredictionPublic(**doc)


def _start_of_today_colombia() -> dt.datetime:
    """Mediodía-noche UTC del día actual en Colombia (América/Bogotá, UTC-5)."""
    now = dt.datetime.now(COLOMBIA_TZ)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start.astimezone(dt.timezone.utc)


def _collect(user, *, min_created: dt.datetime | None = None,
             max_created: dt.datetime | None = None,
             limit: int) -> list[PredictionPublic]:
    db = firebase.db()
    query = db.collection("predictions").where("status", "==", "active")
    if min_created is not None:
        query = query.where("created_at", ">=", min_created)
    if max_created is not None:
        query = query.where("created_at", "<", max_created)

    docs = query.order_by("created_at", direction="DESCENDING").limit(limit).get()

    can_see_premium = user is not None and user.is_premium
    result: list[PredictionPublic] = []
    for snap in docs:
        doc = snap.to_dict()
        if doc.get("premium") and not can_see_premium:
            continue
        result.append(_to_public(doc))
    return result


@router.get("", response_model=list[PredictionPublic])
async def list_predictions(
    league: str | None = Query(default=None),
    user = Depends(get_optional_user),
    _limit: int = Query(default=60, le=120),
) -> list[PredictionPublic]:
    db = firebase.db()
    query = db.collection("predictions").where("status", "==", "active")
    if league:
        query = query.where("league", "==", league)

    docs = query.order_by("created_at", direction="DESCENDING").limit(_limit).get()

    can_see_premium = user is not None and user.is_premium
    result: list[PredictionPublic] = []
    for snap in docs:
        doc = snap.to_dict()
        if doc.get("premium") and not can_see_premium:
            continue
        result.append(_to_public(doc))
    return result


@router.get("/today", response_model=list[PredictionPublic])
async def today_predictions(
    user = Depends(get_optional_user),
) -> list[PredictionPublic]:
    """Pronósticos publicados hoy (día calendario de Colombia)."""
    start = _start_of_today_colombia()
    return _collect(user, min_created=start, limit=40)


@router.get("/history", response_model=list[PredictionPublic])
async def history_predictions(
    user = Depends(get_optional_user),
) -> list[PredictionPublic]:
    """Pronósticos de días anteriores (historial de la app)."""
    start = _start_of_today_colombia()
    return _collect(user, max_created=start, limit=120)


@router.get("/{match_id}/{selection}", response_model=PredictionPublic)
async def get_prediction(
    match_id: str,
    selection: str,
    user = Depends(get_optional_user),
) -> PredictionPublic:
    doc = (
        firebase.db()
        .collection("predictions")
        .document(f"{match_id}_{selection}")
        .get()
    )
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Pronóstico no encontrado.")
    data = doc.to_dict()
    if data.get("premium") and (user is None or not user.is_premium):
        raise HTTPException(status_code=403, detail="Contenido premium.")
    return _to_public(data)