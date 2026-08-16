"""Webhook de pagos de TipsterPage.

TipsterPage notifica las ventas vía HTTP POST firmado. Este endpoint:
1. Verifica la firma HMAC-SHA256 (secret compartido).
2. Normaliza el payload (campos pueden variar según el proveedor).
3. Localiza la orden del usuario y activa premium de forma idempotente.

Durante la Fase 5 se ajusta la normalización con un payload real de prueba.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Header, HTTPException, Request

from app.api import premium as premium_service
from app.core.config import settings
from app.core.security import verify_signature

logger = logging.getLogger("webhooks")

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


def _get(raw: dict, *keys: str) -> object:
    for key in keys:
        if key in raw:
            return raw[key]
    return None


def _dig(raw: dict, path: str) -> object:
    node: object = raw
    for part in path.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node


def _normalize_payload(payload: dict) -> dict | None:
    """Intenta extraer los datos relevantes de cualquier shape de TipsterPage."""
    event = _get(payload, "event", "type", "event_type", "trigger")
    # datos de la venta/transaccion
    sale = (
        _dig(payload, "data.sale")
        or _dig(payload, "sale")
        or _dig(payload, "data.order")
        or _dig(payload, "order")
        or _dig(payload, "data.transaction")
        or _dig(payload, "transaction")
        or _dig(payload, "data.payment")
        or _dig(payload, "payment")
        or payload
    )
    if not isinstance(sale, dict):
        return None

    payment_id = _get(
        sale,
        "payment_id",
        "transaction_id",
        "id",
        "sale_id",
        "charge_id",
        "reference",
    )
    order_id = _get(sale, "order_id", "custom_ref", "custom_reference", "external_reference", "merchant_reference")
    email = _get(
        sale,
        "buyer_email",
        "customer_email",
        "email",
        "payer_email",
        "user_email",
    )
    status = str(_get(sale, "status", "payment_status", "state", "transaction_status", "sale_status") or "").lower()

    return {
        "event": str(event or "").lower(),
        "payment_id": str(payment_id) if payment_id else None,
        "order_id": str(order_id) if order_id else None,
        "email": str(email).lower() if email else None,
        "status": status,
    }


def _is_paid(payload: dict) -> bool:
    normalized = _normalize_payload(payload)
    if not normalized:
        return False
    status = normalized["status"]
    event = normalized["event"]
    paid_keywords = ("paid", "approved", "success", "completed", "succeeded", "accredited", "settled")
    if any(k in status for k in paid_keywords):
        return True
    if any(k in event for k in paid_keywords):
        return True
    return False


@router.post("/tipsterpage")
async def tipsterpage_webhook(
    request: Request,
    x_tipsterpage_signature: str | None = Header(default=None),
    x_hub_signature: str | None = Header(default=None),
    x_webhook_signature: str | None = Header(default=None),
) -> dict:
    signature = (
        x_tipsterpage_signature
        or x_hub_signature
        or x_webhook_signature
        or ""
    )
    body = await request.body()

    if not signature or not verify_signature(body, signature, settings.tipsterpage_webhook_secret):
        raise HTTPException(status_code=401, detail="Firma inválida.")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Body inválido.")

    if not _is_paid(payload):
        return {"received": True, "handled": False, "reason": "not_paid"}

    normalized = _normalize_payload(payload)
    if not normalized or not normalized["payment_id"]:
        raise HTTPException(status_code=400, detail="No se pudo extraer payment_id.")

    order_id = normalized["order_id"]
    try:
        order = premium_service.activate_premium_for_order(
            order_id=order_id or "",
            payment_id=normalized["payment_id"],
            buyer_email=normalized["email"],
        )
    except premium_service.PremiumError as exc:
        # No podemos activar: registramos el fallo para revisión manual.
        logger.warning("Webhook sin activar: %s | payload=%s", exc, normalized)
        return {"received": True, "handled": False, "reason": str(exc)}

    return {"received": True, "handled": True, "order": order["order_id"]}